"""
Service de mise à jour d'Hémicycle ouvert.

n8n appelle   POST /run     (en-tête « Authorization: Bearer <UPDATER_TOKEN> »)
              GET  /status  (même en-tête) : résultat de la dernière exécution
              GET  /health  (sans jeton)

/run : récupère la dernière version du dépôt, lance src/fetch.py puis src/prep.py,
enregistre et pousse sur GitHub si les données ont changé (Dokploy republie alors
le site), et renvoie un compte rendu JSON. Une seule exécution à la fois.

Variables d'environnement :
  UPDATER_TOKEN  jeton partagé avec n8n (obligatoire)
  REPO_SSH       défaut : git@github.com:zenyakwa/hemicycle-ouvert.git
  BRANCH         défaut : main
  DEPLOY_KEY     défaut : /secrets/deploy_key (clé SSH avec droit d'écriture sur le dépôt)
"""
import hmac, json, os, subprocess, threading, time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ.get("UPDATER_TOKEN", "")
REPO = os.environ.get("REPO_SSH", "git@github.com:zenyakwa/hemicycle-ouvert.git")
BRANCH = os.environ.get("BRANCH", "main")
KEY = os.environ.get("DEPLOY_KEY", "/secrets/deploy_key")
WORK = "/work/repo"
ENV = dict(os.environ,
           GIT_SSH_COMMAND=f"ssh -i {KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new",
           GIT_AUTHOR_NAME="scriptek-updater", GIT_COMMITTER_NAME="scriptek-updater",
           GIT_AUTHOR_EMAIL="updater@scriptek.eu", GIT_COMMITTER_EMAIL="updater@scriptek.eu")

lock = threading.Lock()
last = {"status": "never-run"}


def sh(cmd, log, cwd=WORK, timeout=1800):
    log.append("$ " + " ".join(cmd))
    p = subprocess.run(cmd, cwd=cwd, env=ENV, capture_output=True, text=True, timeout=timeout)
    out = (p.stdout + p.stderr).strip()
    if out:
        log.extend(out.splitlines()[-40:])
    if p.returncode != 0:
        raise RuntimeError(f"échec ({p.returncode}) : {' '.join(cmd)}")
    return p.stdout.strip()


def run_update():
    log, t0 = [], time.time()
    result = {"started": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    try:
        if not os.path.isdir(os.path.join(WORK, ".git")):
            sh(["git", "clone", "--depth", "50", "--branch", BRANCH, REPO, WORK], log, cwd="/work")
        sh(["git", "fetch", "origin", BRANCH], log)
        sh(["git", "reset", "--hard", f"origin/{BRANCH}"], log)
        sh(["python", "src/fetch.py"], log)
        sh(["python", "src/prep.py"], log)
        sh(["git", "add", "data", "index.html"], log)
        changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=WORK, env=ENV).returncode != 0
        result["changed"] = changed
        if changed:
            result["files"] = sh(["git", "diff", "--cached", "--stat"], log).splitlines()[-1:]
            day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            sh(["git", "commit", "-m", f"Mise à jour automatique des données ({day}, serveur Scriptek)"], log)
            sh(["git", "push", "origin", f"HEAD:{BRANCH}"], log)
            result["commit"] = sh(["git", "rev-parse", "--short", "HEAD"], log)
        result["status"] = "ok"
    except Exception as e:  # compte rendu lisible par n8n
        result["status"] = "error"
        result["error"] = str(e)
    result["duration_s"] = round(time.time() - t0)
    result["log_tail"] = log[-25:]
    return result


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self):
        got = self.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        return bool(TOKEN) and hmac.compare_digest(got, TOKEN)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True, "busy": lock.locked()})
        if not self._authorized():
            return self._send(401, {"error": "jeton manquant ou invalide"})
        if self.path == "/status":
            return self._send(200, last)
        self._send(404, {"error": "inconnu"})

    def do_POST(self):
        global last
        if not self._authorized():
            return self._send(401, {"error": "jeton manquant ou invalide"})
        if self.path != "/run":
            return self._send(404, {"error": "inconnu"})
        if not lock.acquire(blocking=False):
            return self._send(409, {"status": "busy", "error": "une mise à jour est déjà en cours"})
        try:
            last = run_update()
        finally:
            lock.release()
        self._send(200 if last["status"] == "ok" else 500, last)

    def log_message(self, fmt, *args):
        print("%s %s" % (self.address_string(), fmt % args), flush=True)


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("UPDATER_TOKEN manquant")
    os.makedirs("/work", exist_ok=True)
    print("Service de mise à jour prêt sur :8080", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

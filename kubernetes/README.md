# Kubernetes Basics - Lernzusammenfassung

> **Status:** ✅ Abgeschlossen (Phase 1 meines DevOps-Lehrplans)

## Was ist Kubernetes?

Kubernetes (K8s) ist ein Container-Orchestrierungssystem. Es verwaltet Container über mehrere Server/VMs hinweg: startet sie, verteilt sie, überwacht sie und heilt sich selbst bei Ausfällen.

## Lokales Setup

**Mein Setup:** Debian WSL + Docker + Minikube + kubectl

```
┌─────────────────────────────────────────────────┐
│  Mein Rechner (WSL)                             │
│                                                 │
│   kubectl ──────► Minikube-Cluster              │
│      │            (läuft als Docker-Container)  │
│      │                                          │
│      └── liest ~/.kube/config                   │
│          (von Minikube konfiguriert)            │
└─────────────────────────────────────────────────┘
```

- **kubectl:** CLI-Tool, spricht den Kubernetes API-Server an
- **Minikube:** Erstellt einen lokalen Single-Node-Cluster (perfekt zum Lernen)
- **~/.kube/config:** Enthält Cluster-Verbindungsdaten (von Minikube automatisch gesetzt)

## Cluster-Architektur

```
Cluster
├── Control Plane (Gehirn)
│   ├── API Server      ← kubectl spricht hiermit
│   ├── etcd            ← Datenbank für Cluster-Zustand
│   ├── Scheduler       ← Entscheidet: welcher Pod auf welchen Node?
│   └── Controller Manager ← Überwacht und korrigiert Zustand
│
└── Worker Nodes (Arbeiter)
    └── Pods
        └── Container(s)
```

## Ressourcen-Hierarchie

### Deployment → ReplicaSet → Pod

```
Deployment (was ich definiere)
    │
    │ erstellt automatisch
    ▼
ReplicaSet (sorgt für gewünschte Anzahl Pods)
    │
    │ erstellt/löscht bei Bedarf
    ▼
Pod(s) (kleinste deploybare Einheit)
    │
    └── Container (das eigentliche Image)
```

**Wichtig:** 
- Ich arbeite mit Deployments, nicht direkt mit Pods
- Das ReplicaSet ist implizit – es sorgt für Self-Healing
- Pods sind ephemeral (kurzlebig), können jederzeit ersetzt werden

## Services - Netzwerk-Zugriff auf Pods

Pods bekommen dynamische IPs und können jederzeit sterben. **Services** bieten eine stabile Adresse.

### Service-Typen

| Typ | Erreichbar von | Use Case |
|-----|----------------|----------|
| **ClusterIP** | Nur innerhalb des Clusters | Datenbanken, interne APIs |
| **NodePort** | Außerhalb via `<NodeIP>:<Port>` | Entwicklung, Tests |
| **LoadBalancer** | Außerhalb via Cloud-LB | Produktion (AWS, GCP, Azure) |

### Verbindung Service → Pods

```yaml
# Service
selector:
  app: wordpress    # ← Findet alle Pods mit diesem Label

# Deployment/Pod
labels:
  app: wordpress    # ← Wird vom Service gefunden
```

**Service Discovery im Cluster:** Pods können andere Services über DNS erreichen:
```
mysql-svc          # Service-Name reicht
mysql-svc.default  # Mit Namespace
```

## Konfiguration externalisieren

### Secrets (sensible Daten)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
type: Opaque
data:
  mysql-password: cGFzc3dvcmQxMjM=  # Base64-encoded
```

**Wichtig:** Base64 ist Encoding, keine Verschlüsselung! Secrets bieten:
- Semantische Trennung von ConfigMaps
- Separate RBAC-Regeln möglich
- Nicht im Klartext in `kubectl get`

### ConfigMaps (nicht-sensible Konfiguration)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DB_HOST: "mysql-svc"
  LOG_LEVEL: "info"
```

### Verwendung in Pods

```yaml
env:
  - name: MYSQL_PASSWORD
    valueFrom:
      secretKeyRef:
        name: mysql-secret
        key: mysql-password
  - name: DB_HOST
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: DB_HOST
```

**⚠️ Wichtig:** Änderungen an Secrets/ConfigMaps erfordern Pod-Neustart:
```bash
kubectl rollout restart deployment <name>
```

## Persistente Daten

Pods sind kurzlebig – Daten müssen extern gespeichert werden.

```
PersistentVolume (PV)          PersistentVolumeClaim (PVC)
├── Vom Platform-Team          ├── Vom Entwickler
├── "Hier ist Speicher"        ├── "Ich brauche 1Gi"
└── Abstraktion über Backend   └── Wird an PV gebunden
```

```yaml
# PVC (eigene Ressource, separate YAML)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 1Gi

# Im Deployment referenzieren
volumes:
  - name: mysql-storage
    persistentVolumeClaim:
      claimName: mysql-pvc
```

**StorageClass** abstrahiert das Backend:
- Minikube: `hostpath` (lokaler Ordner)
- AWS: `gp3` (EBS Volume)
- YAML bleibt portabel!

## Namespaces - Cluster unterteilen

Namespaces sind isolierte Bereiche innerhalb eines Clusters.

```bash
kubectl get namespaces
# default         ← Meine Ressourcen (Standard)
# kube-system     ← Kubernetes-interne Komponenten
# kube-node-lease ← Node-Heartbeats
# kube-public     ← Öffentliche Infos
```

### Vorteile

| Feature | Beschreibung |
|---------|--------------|
| **Namens-Isolation** | Gleiche Namen in verschiedenen Namespaces möglich |
| **Zugriffskontrolle** | RBAC-Rechte pro Namespace |
| **Ressourcenlimits** | CPU/RAM-Quotas pro Namespace |

```yaml
# Namespace im Manifest definieren
metadata:
  name: mysql-deployment
  namespace: wordpress-project
```

```bash
# Namespace bei Befehlen angeben
kubectl get pods -n wordpress-project
kubectl get pods --all-namespaces  # oder: kubectl get pods -A
```

## Wichtige kubectl-Befehle

```bash
# Ressourcen anzeigen
kubectl get pods|deployments|services|secrets|configmaps|pvc
kubectl get all                    # Alle Ressourcen
kubectl get pods -A                # Alle Namespaces

# Details & Debugging
kubectl describe pod <name>        # Detailinfos + Events
kubectl logs <pod-name>            # Container-Logs
kubectl exec <pod> -- <command>    # Befehl im Container ausführen

# Ressourcen erstellen/ändern
kubectl apply -f <datei.yaml>      # Deklarativ (empfohlen)
kubectl apply -f <ordner>/         # Alle YAMLs im Ordner
kubectl delete -f <datei.yaml>     # Ressource löschen

# Deployments verwalten
kubectl rollout restart deployment <name>  # Pods neu starten
kubectl scale deployment <name> --replicas=3
```

## Projekt: WordPress + MySQL

Mein erstes Multi-Service-Deployment:

```
wordpress-project (Namespace)
│
├── mysql-secret        ← DB-Credentials
├── wordpress-config    ← ConfigMap für WordPress
├── mysql-pvc           ← Persistenter Speicher
│
├── mysql-deployment    ← MySQL Pod
├── mysql-svc           ← ClusterIP Service
│
├── wordpress-deployment ← WordPress Pod
└── wordpress-svc        ← NodePort Service (extern erreichbar)
```

**Gelernt dabei:**
- Service Discovery via DNS (`mysql-svc`)
- Secrets für Passwörter, ConfigMaps für Konfiguration
- PVC für Datenbank-Persistenz
- Namespace für Projekt-Isolation

---

## Erkenntnisse

1. **Deklarativ > Imperativ** – YAML-Manifests statt `kubectl run`
2. **Pods sind ephemeral** – Services bieten Stabilität
3. **Labels verbinden** – Services finden Pods über Selektoren
4. **Konfiguration raus aus Images** – Secrets & ConfigMaps
5. **Kubernetes heilt sich selbst** – ReplicaSets ersetzen tote Pods

---

*Dokumentiert während meiner DevOps-Lernreise, Januar 2025*
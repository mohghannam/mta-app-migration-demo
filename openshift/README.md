# OpenShift deployment

## Prerequisites

- OpenShift 4.x cluster
- `oc` logged in as a user allowed to create resources in `mtc-demo`
- A storage class capable of provisioning RWO PVCs
- Access to the Red Hat registry used by the PostgreSQL image

## 1. Create the project

    oc apply -f namespace.yaml
    oc project mtc-demo

## 2. Create application configuration and storage

    oc apply -f secret.yaml
    oc apply -f postgres-pvc.yaml
    oc apply -f uploads-pvc.yaml

## 3. Deploy PostgreSQL

    oc apply -f postgres.yaml

Wait for it:

    oc rollout status deployment/postgres

## 4. Build the application

Create the BuildConfig/ImageStream:

    oc apply -f buildconfig.yaml

From the repository root, start a binary build:

    oc start-build task-portal --from-dir=. --follow

## 5. Deploy the application

    oc apply -f app.yaml
    oc rollout status deployment/task-portal

Get the route:

    oc get route task-portal

## 6. Populate demo data

Open the route and:

- Add several tasks.
- Upload a few documents/images.
- Optionally change the seeded task data.

The task rows are stored in PostgreSQL PVC `postgres-data`.
Uploaded files are stored in PVC `app-uploads`.

## Important MTC note

MTC normally migrates a namespace as a unit. Keep all of the application's objects in this namespace:

    mtc-demo

This makes it easy to select the namespace in the MTC Migration Plan.

## Validation commands

    oc get pods,pvc,svc,route
    oc get deployment
    oc get secret mtc-demo-db

To inspect PostgreSQL data:

    oc exec deployment/postgres -- bash -c 'psql -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -c "select id,title,owner,status from tasks order by id;"'

To inspect uploaded files:

    oc exec deployment/task-portal -- ls -lah /app/uploads

## Migration demonstration

Before migration, record:

    oc get pvc
    oc get pods
    oc get route

Open the application and note the tasks and uploaded files.

Then create an MTC migration plan:

- Source cluster: this cluster
- Destination cluster: target OpenShift cluster
- Namespace: `mtc-demo`
- Include persistent volumes
- Run the migration

After migration, verify on the destination:

    oc project mtc-demo
    oc get pods,pvc,svc,route
    oc get route task-portal

Open the new route and demonstrate that:

1. The tasks still exist.
2. Uploaded files still exist.
3. PostgreSQL contains the same records.
4. The application is running on the destination cluster.

## Suggested demo story

Create a task called:

    Production cutover

Upload a file called:

    migration-evidence.txt

Put the following text in it:

    This file was created on the source OpenShift cluster.
    If you can download it after migration, persistent storage was migrated successfully.

Then migrate the namespace and download the same file from the destination.

# OpenShift MTC Stateful Application Demo

A deliberately small stateful application designed to demonstrate the application migration capabability mta-ops in the Migration Toolkit for Applications.

## Architecture

    Customer Task Portal
             |
       +-----+------+
       |            |
    Flask        PostgreSQL
       |            |
    uploads       PVC
      PVC

The namespace contains:

- Flask/Gunicorn web application
- PostgreSQL database
- PostgreSQL PVC
- Uploads PVC
- Secret
- Services
- Route

## Why two PVCs?

This makes the MTC demonstration visually clear:

- `postgres-data` contains relational application state.
- `app-uploads` contains user-generated files.

After migration, both should contain the same data.


## Build Application Image
The image is built from the DockerFile using the podman command below. I am using quay.io to host the image. You may need to change the deployment to reference the location you choose to host the image at.
    podman build -t task-portal .
## Fast deployment

From this directory:

    oc apply -f openshift/namespace.yaml
    oc project mtc-demo
    oc apply -f openshift/secret.yaml
    oc apply -f openshift/quay-robot-secret.yaml
    oc apply -f openshift/postgres-pvc.yaml
    oc apply -f openshift/uploads-pvc.yaml
    oc apply -f openshift/postgres.yaml
    oc rollout status deployment/postgres
    oc apply -f openshift/app.yaml
    oc rollout status deployment/task-portal
    oc get route task-portal

## Demo flow

1. Deploy on Cluster A.
2. Open the application.
3. Add tasks.
4. Upload documents.
5. Show the two PVCs.
6. Use mta-ops to migrate `mtc-demo` to Cluster B.
7. Validate pods, services, route and PVCs.
8. Open the application on Cluster B.
9. Show that tasks and uploaded documents survived.


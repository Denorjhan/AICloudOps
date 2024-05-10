#!/bin/bash

kubectl create namespace app

kubectl create secret generic chatbot-env --from-env-file=.env --namespace=app

helmfile sync -f k8s/helmfile.yaml 

# deply postgres, rabbitmq, chatbot, logger
kubectl apply -f k8s/manifests/ --namespace=app --recursive


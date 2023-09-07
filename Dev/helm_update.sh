#!/bin/bash
echo "Helm Update"
version=$1

echo "Replace tag version into Helm values.yaml $version"
helmValues=$(<./helm/values.yaml)
helmValues=$(echo "$helmValues" | sed -r 's/tag: "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"/tag: "'$version'"/gi')
echo "$helmValues" > ./helm/values.yaml
cat ./helm/values.yaml

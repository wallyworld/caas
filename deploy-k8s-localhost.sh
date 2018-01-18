#!/bin/bash -e

if [ $# -lt 3 ]; then
    echo "Usage: deployk8slocalhost.sh <controller> <model> <path-to-k8-bundle>"
    exit
fi

controller=$1
model=$2
k8bundle=$3

#JUJU_DEV_FEATURE_FLAGS=caas,developer-mode juju bootstrap --debug lxdq $controller 

juju add-model $model

profile=$(cat <<'EOF'
name: juju-##MODEL##
config:
  boot.autostart: "true"
  linux.kernel_modules: ip_tables,ip6_tables,netlink_diag,nf_nat,overlay
  raw.lxc: |
    lxc.aa_profile=unconfined
    lxc.mount.auto=proc:rw sys:rw
    lxc.cap.drop=
  security.nesting: "true"
  security.privileged: "true"
description: ""
devices:
  aadisable:
    path: /sys/module/nf_conntrack/parameters/hashsize
    source: /dev/null
    type: disk
  aadisable1:
    path: /sys/module/apparmor/parameters/enabled
    source: /dev/null
    type: disk
EOF
       )

echo "$profile" | lxc profile edit juju-$model

juju deploy $k8bundle

#read -p"Press return to watch deployment status, hit ctrl-C when everything's done." x
watch -c juju status --color

juju scp -m "$controller:$model" kubernetes-master/0:config ~/.kube/config

kubectl get all

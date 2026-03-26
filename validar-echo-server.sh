#!/bin/bash
msg="Test_Echo_Message_123"
network="tp0_testing_net"

resp=$(docker run --rm --network "$network" busybox sh -c "echo '$msg' | nc server 12345")

if [ "$resp" = "$msg" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
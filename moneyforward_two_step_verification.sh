#!/bin/bash

session_cookie=~/cookies/moneyforward_session.cookie

user_agent="Mozilla/5.0"
verification_code=$1

readonly program=$(basename $0)

function print_usage_and_exit() {
  echo >&2 "Usage: ${program} verification_code"
  exit 1
}

if [ $# -ne 1 ]; then
  print_usage_and_exit
fi

curl \
-A $user_agent \
-X GET \
--dump-header - \
-b $session_cookie \
-s \
https://moneyforward.com/users/two_step_verifications/verify/$verification_code


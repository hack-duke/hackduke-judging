# HackDuke Judging Backend

Basic manual testing of the endpoints:

```

curl -H "Content-Type: application/json" -X POST -d '{"num_alts":"100"}' http://localhost:5000/init

curl -H "Content-Type: application/json" -X POST -d '{"judge_id":"judge_1"}' http://localhost:5000/get_decision

curl -H "Content-Type: application/json" -X POST -d '{"judge_id":"judge_1", "favored": "CHOICE_A"}' http://localhost:5000/perform_decision

curl http://localhost:5000/results

```


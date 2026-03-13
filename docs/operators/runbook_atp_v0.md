# Runbook ATP v0

Runbook M5 cho ATP:

1. tiep nhan request file
2. normalize request
3. classify request
4. resolve product qua registry/profile/policy
5. build task manifest va product context
6. tao evidence bundle preview
7. prepare route tu capability/provider/node registry
8. select provider + node route
9. xem summary tren CLI

Supported products hien tai:

- `ATP`
- `TDF`

Van hanh v0:

- routing chi dung data dang co trong ATP flow va registry ATP
- uu tien `non_llm_execution` + `local_mac` khi capability phu hop
- khong thuc thi adapter hay command
- `run` van chi la preview, chua execute pipeline

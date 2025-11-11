## :warning: Please read these instructions carefully and entirely first
* Clone this repository to your local machine.
* Use your IDE of choice to complete the assignment.
* When you have completed the assignment, you need to  push your code to this repository and [mark the assignment as completed by clicking here](https://app.snapcode.review/submission_links/e0990499-78c8-4f23-ae8e-ad484b792d43).
* Once you mark it as completed, your access to this repository will be revoked. Please make sure that you have completed the assignment and pushed all code from your local machine to this repository before you click the link.

## Operability Take-Home Exercise

Welcome to the start of our recruitment process for Operability Engineers. It was great to speak to you regarding an opportunity to join the Equal Experts network!

Please write code to deliver a solution to the problems outlined below.

We appreciate that your time is valuable and do not expect this exercise to **take more than 90 minutes**. If you think this exercise will take longer than that, I **strongly** encourage you to please get in touch to ask any clarifying questions.

### Submission guidelines
**Do**
- Provide a README file in text or markdown format that documents a concise way to set up and run the provided solution.
- Take the time to read any applicable API or service docs, it may save you significant effort.
- Make your solution simple and clear. We aren't looking for overly complex ways to solve the problem since in our experience, simple and clear solutions to problems are generally the most maintainable and extensible solutions.

**Don't**

Expect the reviewer to dedicate a machine to review the test by:

- Installing software globally that may conflict with system software
- Requiring changes to system-wide configurations
- Providing overly complex solutions that need to spin up a ton of unneeded supporting dependencies. We aspire to keep our dev experiences as simple as possible (but no simpler)!
- Include identifying information in your submission. We are endeavouring to make our review process anonymous to reduce bias.

### Exercise
If you have any questions on the below exercise, please do get in touch and we’ll answer as soon as possible.

#### Build an API, test it, and package it into a container
- Build a simple HTTP web server API in any general-purpose programming language[^1] that interacts with the GitHub API and responds to requests on `/<USER>` with a list of the user’s publicly available Gists[^2].
- Create an automated test to validate that your web server API works. An example user to use as test data is `octocat`.
- Package the web server API into a docker container that listens for requests on port `8080`. You do not need to publish the resulting container image in any container registry, but we are expecting the Dockerfile in the submission.
- The solution may optionally provide other functionality (e.g. pagination, caching) but the above **must** be implemented.

Best of luck,  
Equal Experts
__________________________________________
[^1]: For example Go, Python or Ruby but not Bash or Powershell.  
[^2]: https://docs.github.com/en/rest/gists/gists?apiVersion=2022-11-28


#### SETUP

Run locally (without Docker)

Create a venv and install:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


Run server:

python main.py
# Server listens on http://0.0.0.0:8080


Test manually:

curl -v http://127.0.0.1:8080/octocat


You should receive JSON with source: "github" and gists list.

Run tests
pytest -q


The tests mock GitHub's API so they are deterministic and fast.

Build & run with Docker
# build
docker build -t gists-proxy:latest .

# run (map host port 8080 to container 8080)
docker run --rm -p 8080:8080 gists-proxy:latest


Then:

curl http://localhost:8080/octocat


Optional: provide a GITHUB_TOKEN env var to the container for higher GitHub rate limits:

docker run --rm -p 8080:8080 -e GITHUB_TOKEN=ghp_xxx gists-proxy:latest

Notes / features & limitations

The server calls GitHub's public API: GET https://api.github.com/users/{user}/gists.

Basic error handling: 404 from GitHub returns 404 to the client; other upstream errors return appropriate 5xx/4xx.

Simple in-memory TTL caching (default 30 seconds) to reduce repeat requests. TTL configurable via CACHE_TTL_SECONDS env var.

The response includes a compact summary per gist: id, url, description, files (list of filenames), created_at, updated_at.

No persistence — the cache is in memory (suitable for this assignment). For production, prefer Redis or similar.

Rate-limiting isn't implemented; use GITHUB_TOKEN to increase GitHub rate limits if testing heavily.

If you want, I can:

Convert this to FastAPI + automatic OpenAPI docs,

Add pagination support (accept ?page=...&per_page=... and forward to GitHub),

Add a simple integration test that runs a container and hits the endpoint (CI style),

Or produce a single tar.gz that contains all files ready for submission.

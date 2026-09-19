# The agent seats' workstation image (Stage 1 containerization, ADR
# pending; owner order 2026-09-18). One prebaked environment so no run
# spends its first minutes installing what every run needs, and no two
# runs drift apart. Built by .github/workflows/build-agent-image.yml
# into ghcr.io/alexandrapaiz/alexandria-agent.

FROM node:20-bookworm

# Base tooling every seat reaches for: git and curl (plumbing), python3
# (scripts and conflict resolution), postgres client (NEON_RO_URL
# queries), jq (gh --json work).
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates python3 python3-pip postgresql-client jq \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI, from GitHub's own apt repo.
RUN mkdir -p -m 755 /etc/apt/keyrings \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg -o /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# Playwright's Chromium, preinstalled at a fixed path so the frontend
# seat's visual-verification law costs seconds, not minutes. Pin the
# playwright version when site/package.json pins one.
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN npx --yes playwright@1.49.1 install --with-deps chromium \
    && rm -rf /root/.npm \
    && chmod -R a+rX /ms-playwright

# The seats run as the image's non-root user (uid 1000): Claude Code
# refuses bypassPermissions under root, by design, and it is the right
# posture anyway. The workflows pass --user 1000:1000; everything the
# runs need at runtime is already installed above.

CMD ["/bin/bash"]

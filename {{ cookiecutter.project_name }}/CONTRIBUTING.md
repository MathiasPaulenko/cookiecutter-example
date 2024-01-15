# Contributing to TalosBDD

The TalosBDD Automation Framework welcomes contributions from everyone. There are a number of ways you can help:

## Bug Reports

When opening new issues or commenting on existing issues please make sure discussions are related to concrete technical
issues with the TalosBDD Automation Framework.

It's imperative that issue reports outline the steps to reproduce the defect. If the issue can't be reproduced it will
be closed. Please provide [concise reproducible test cases](http://sscce.org/)
and describe what results you are seeing and what results you expect.

Issues shouldn't be used for support. Please address questions to the
[TalosBDD Support Team Channel](https://teams.microsoft.com/l/channel/19%3a81ededf4d389425f92d3ff4bcf49f7b5%40thread.skype/Talos%2520BDD?groupId=66e4a0f7-e684-4a3a-b47e-e583edfe295b&tenantId=35595a02-4d6d-44ac-99e1-f9ab4cd872db).

## Bug Resolution

You can also contribute to the resolution of existing bugs in the channels or in the repositories.

Bug fixes will be carried out following the [Collaboration and development process](#code-contributions) flow.

The Talos team will help you and guide you in solving the bug via
the [TalosBDD Contributions Team Channel](https://teams.microsoft.com/l/channel/19%3aedc0959bbd064f8abd249f32c8ed3fb5%40thread.skype/Contributions?groupId=66e4a0f7-e684-4a3a-b47e-e583edfe295b&tenantId=35595a02-4d6d-44ac-99e1-f9ab4cd872db).

## Feature or Integration Requests

If you find that TalosBDD is missing something, feel free to open an issue with details describing what feature(s) you'd
like added or changed.

Please address questions to the [TalosBDD Contributions Team Channel](https://teams.microsoft.com/l/channel/19%3aedc0959bbd064f8abd249f32c8ed3fb5%40thread.skype/Contributions?groupId=66e4a0f7-e684-4a3a-b47e-e583edfe295b&tenantId=35595a02-4d6d-44ac-99e1-f9ab4cd872db)
to in order to comment on the new feature or integration you need.

## Implementation of New Feature or Integration

You can also contribute to the implementation of existing features and integrations in channels or repositories.

The implementation of the features or integration will be carried out following
the [Collaboration and development process](#code-contributions) flow seen above.

The Talos team will assist and guide you through the implementation via
the [TalosBDD Contributions Team Channel](https://teams.microsoft.com/l/channel/19%3aedc0959bbd064f8abd249f32c8ed3fb5%40thread.skype/Contributions?groupId=66e4a0f7-e684-4a3a-b47e-e583edfe295b&tenantId=35595a02-4d6d-44ac-99e1-f9ab4cd872db).

## Documentation

TalosBDD is a big Automation Framework and documentation is key to understanding how things work and learning effective
ways to exploit its potential.

If you find a functionality, a usage or any topic related to any of the tools that is not currently documented, you can
generate this documentation and send it to the Talos team for uploading to the official documentation repository.

You can share documentation in docx, pdf, html or video via
the [TalosBDD Contributions Team Channel](https://teams.microsoft.com/l/channel/19%3aedc0959bbd064f8abd249f32c8ed3fb5%40thread.skype/Contributions?groupId=66e4a0f7-e684-4a3a-b47e-e583edfe295b&tenantId=35595a02-4d6d-44ac-99e1-f9ab4cd872db)

## Resolution of issues and Doubts in the Channel.

The Talos team is always open to question, but it is always good to have several points of view.

Feel free to comment and give your solution in the thread of any channel doubt message.

## Disclosures and Channel Events.

The Talos team will make disclosures and events to explain, teach or showcase features, functionalities or any topic
related to Talos tools.

Feel free to participate in this dissemination and events on the topics in which you are an expert speaker.

Ask for topics for the Talos team to address at such outreach and events.

Participate openly in any outreach and events about your questions, needs or improvements to the TalosBDD framework.

## Code Contributions

This document will guide you through the contribution process.

### Step 1: Fork

Fork the project [on Github](https://github.com/seleniumhq/selenium) and check out your copy locally.

```shell
% git clone git@github.alm.europe.cloudcenter.corp:username/talosbdd.git --depth 1
% cd talosbdd
% git remote add upstream git://github.alm.europe.cloudcenter.corp/sgt-talos/python-talos-talos-bdd.git
```

We do accept help in upgrading our existing dependencies or removing superfluous dependencies. If you need to add a new
dependency it's often a good idea to reach out to the Talos Team to check that your approach aligns with the project's
ideas. Nothing is more frustrating than seeing your hard work go to waste because your vision doesn't align with the
project's.

### Step 2: Branch

Create a feature branch and start hacking:

```shell
% git checkout -b my-feature-branch
```

### Step 3: Commit

**Writing good commit messages is important.** A commit message should describe what changed, why, and reference issues
fixed (if any).

```shell
% git commit -m "a very good commit message"
```

### Step 4: Pull Request

Go to Github and create a new pull request from your added feature branch to the development branch of the TalosBDD core
repository.

Remember to fill in the Pull Request application form clearly and efficiently.

## Communication

- [TalosBDD Support Team Channel](https://teams.microsoft.com/l/channel/19%3a81ededf4d389425f92d3ff4bcf49f7b5%40thread.skype/Talos%2520BDD?groupId=66e4a0f7-e684-4a3a-b47e-e583edfe295b&tenantId=35595a02-4d6d-44ac-99e1-f9ab4cd872db)
- [TalosBDD Contributions Team Channel](https://teams.microsoft.com/l/channel/19%3aedc0959bbd064f8abd249f32c8ed3fb5%40thread.skype/Contributions?groupId=66e4a0f7-e684-4a3a-b47e-e583edfe295b&tenantId=35595a02-4d6d-44ac-99e1-f9ab4cd872db)
- [TalosBDD Github Issues Section](https://github.alm.europe.cloudcenter.corp/sgt-talos/python-talos-talos-bdd/issues)

# Mozilla.ai Lumigator

Lumigator is an open-source platform built by [Mozilla.ai](https://www.mozilla.ai/) for guiding users through the process of selecting the right language model for their needs.
Currently, we support evaluating summarization tasks using sequence-to-sequence models like BART and BERT and causal architectures like GPT and Mistral,
but will be expanding to other machine learning tasks and use-cases.

See [example notebook](/notebooks/walkthrough.ipynb) for full platform API walkthrough.

## Docs:

+ **Installing Lumigator**
  + Building
    + [Pants guide](PANTS_GUIDE.md)
  + Using/Testing
    + [Kubernetes Helm Charts](lumigator/infra/mzai/helm/lumigator/README.md)
    + [Local install documentation](/.devcontainer/README.md)
+ **Using Lumigator:**
  + [Platform Examples](/notebooks/walkthrough.ipynb)
  + [Lumigator API](/lumigator/README.md)
  + Offline Evaluations with [lm-buddy](https://github.com/mozilla-ai/lm-buddy)
  + Online Evaluations with [Ray Serve Deployments](lumigator/python/mzai/summarizer/README.md)
+ **Understanding Evaluation**
  + [Evaluating Large Language Models](/EVALUATION_GUIDE.md)

## Platform Setup

## Available Machine Learning Tasks

 - Summarization

## Available Models for Online Ground Truth Generation

| Model Type | Model                                        | via HuggingFace | via API |
|------------|----------------------------------------------|-----------------|---------|
| seq2seq    | facebook/bart-large-cnn                      |       X         |         |
| causal     | gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo-0125 |                 |    X    |
| causal     | open-mistral-7b                              |                 |    X    |


## Available Models for Offline Evaluation:

| Model Type | Model                                        | via HuggingFace | via API |
|------------|----------------------------------------------|-----------------|---------|
| seq2seq    | facebook/bart-large-cnn                      |       X         |         |
| seq2seq    | longformer-qmsum-meeting-summarization       |       X         |         |
| seq2seq    | mrm8488/t5-base-finetuned-summarize-news     |       X         |         |
| seq2seq    | Falconsai/text_summarization                 |       X         |         |
| causal     | gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo-0125 |                 |    X    |
| causal     | open-mistral-7b                              |                 |    X    |


## Available Metrics:

+ ROUGE - (Recall-Oriented Understudy for Gisting Evaluation), which compares an automatically-generated summary to one generated by a machine learning model on a score of 0 to 1 in a range of metrics comparing statistical similarity of two texts.
+ METEOR - Looks at the harmonic mean of precision and recall
+ BERTScore - Generates embeddings of ground truth input and model output and compares their cosine similarity

[Check this link](notebooks/assets/metrics.png) for a list of pros and cons of each metric and an example of how they work

> [!NOTE]
>
> Lumigator is in the early stages of development.
> It is missing important features and documentation.
> You should expect breaking changes in the core interfaces and configuration structures
> as development continues.

# Technical Overview

Lumigator is a Python-based FastAPI web app with REST API endpoints that allow for access to services for serving and evaluating large language models available as safetensor artifacts hosted on both HuggingFace and local stores, with our first primary focus being Huggingface access, and tracking the lifecycle of a model in the backend database (Postgres).
It consists of:

+ a FastAPI-based huggingface's `evaluate` library for those metrics, but we are considering using lm-harness that manages platform activity backed by Postgres
+ online evaluation of models using **Ray Serve** deployments
+ a **Ray cluster** to run offline evaluation jobs using [lm-buddy](https://github.com/mozilla-ai/lm-buddy), our in-house eval framework
    + LM buddy spins up a vLLM deployment using Ray Serve for inference/evalution jobs and the core of evaluation happens using huggingface's `evaluate` library for those metrics, but we are evaluating lm-eval-harness, as well
+ Artifact management (S3 in the cloud, localstack locally )
+ A Postgres database to track platform-level tasks and dataset metadata

# Get Started

You can build the local project using `pants` and `docker-compose`,  or into a distributed environment using Kubernetes [`Helm charts`](lumigator/infra/mzai/helm/lumigator/README.md)

## Local Development Setup (Currently targeting Mac)
1. `git clone` repo
2.  Install pants using homebrew `brew install pantsbuild/tap/pants` . For more on using Pants, read the [Pants guide](PANTS_GUIDE.md).
3. `make bootstrap-dev-environment`
4. `make local-up`. For more on `docker-compose`, see the [local install documentation.](/.devcontainer/README.md).

### Dev Environment Details
This includes a standalone python interpreter, venv (`mzaivenv`), precommit configs, and more. Python setup is
handled by `uv`; pants maintains lockfiles for different platforms. Currently, only `python 3.11.9` is valid for this project; if a compatible interpreter
is found `uv` will not download a standalone python interpreter for you.

For VSCode users, activate the venv before opening your IDE; the `.env` file will be recognized automatically.


```shell
make bootstrap-dev-environment
source mzaivenv/bin/activate
```

Show targets:

```bash
make show-pants-targets
```

run the app locally via docker compose:

```bash
make local-up
make local-logs # gets the logs from docker compose
make local-down # shuts it down
```

Compile targets manually:

```bash
pants package <target>
# backend app
pants package lumigator/python/mzai/backend --no-local-cache
# backend docker image
pants package lumigator/python/mzai/backend:backend_image
```

### Environment variable reference

If the S3 storage service is used, some environment variables are needed to connect to it. Additionally, models from Mistral or OpenAI can be used via API instead of instantiating them within Lumigator. In this case, the corresponding key is needed.

| Environment variable name | Default value | Description |
| --- | :-: | --- |
| LOCAL_FSSPEC_S3_ENDPOINT_URL | "" | Endpoint URL for the S3 data storage service |
| LOCAL_FSSPEC_S3_KEY | "" | Key for the S3 data storage service |
| LOCAL_FSSPEC_S3_SECRET | "" | Secret for the S3 data storage service |
| MISTRAL_API_KEY | "" | Key for Mistral API models |
| OPENAI_API_KEY | "" | Key for OpenAI API models |
| LOCALSTACK_AUTH_TOKEN | "" | Authentication token for the LocalStack service |

## Rebuilding dependencies

You may need to manually regenerate the [lockfiles](https://www.pantsbuild.org/2.21/docs/python/overview/lockfiles) if you update dependencies.
To do so:

1. Add your new dependency to `3rdparty/python/pyproject.toml`. This file respects system platform markers, and only very special cases need to be added as explicit `python_requirement` targets.
2. run `pants generate-lockfiles`. This will take a while - 5-10 minutes in some cases and require access to pypi.

make sure to add the new lockfiles to the repo with your PR. You'll have to rebuild your dev environment if you haven't already.


import asyncio
from http import HTTPMethod
from uuid import UUID

from schemas.extras import ListingResponse
from schemas.jobs import (
    JobCreate,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
    JobType,
)

from sdk.client import ApiClient


class Jobs:
    JOBS_ROUTE = "jobs"

    def __init__(self, c: ApiClient):
        """Construct a new instance of the Jobs class.

        Args:
            c (ApiClient): the API client to use for requests.

        Returns:
            Jobs: a new Jobs instance.
        """
        self.client = c

    def get_jobs(self) -> ListingResponse[JobResponse]:
        """Return information on all jobs.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.jobs.get_jobs()

        Returns:
            ListingResponse[JobResponse]: All existing jobs.
        """
        response = self.client.get_response(self.JOBS_ROUTE)

        if not response:
            return []

        return ListingResponse[JobResponse](**response.json())

    def get_job(self, id: UUID) -> JobResponse:
        """Return information on a specific job.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.jobs.get_job(job_id)

        Args:
            id (UUID): the ID of the job to retrieve
        Returns:
            JobResponse: The job information for the provided ID.
        """
        response = self.client.get_response(f"{self.JOBS_ROUTE}/{id}")

        if not response:
            return []

        return JobResponse(**(response.json()))

    async def wait_for_job(self, id: UUID, retries: int = 30, poll_wait: int = 30) -> JobResponse:
        """Wait for a job to succeed and return latest retrieved information.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                job = lm_client.jobs.wait_for_job(job_id)  # Create the coroutine object
                result = await job  # Await the coroutine to get the result

        Args:
            id (UUID): The ID of the job to wait for.
            retries (int): The number of times to poll for the job status.
            poll_wait (int): The time to wait between polling attempts.

        Returns:
            JobResponse: the most recently job information for the ID, when the
              job has finished
        """
        for _ in range(1, retries):
            # http://localhost:8265/api/jobs/f311fa44-025a-4703-b8ba-7e0b1001b484
            response = self.client.get_ray_job_response(f'{id}')
            # response = requests.get(f"http://localhost:8265/api/jobs/{id}")
            jobinfo = response.json()
            if jobinfo["status"] == "PENDING" or jobinfo["status"] == "RUNNING":
                await asyncio.sleep(poll_wait)
                continue
            elif jobinfo["status"] == "FAILED":
                raise Exception(f"Job {id} failed")
            elif jobinfo["status"] == "STOPPED":
                raise Exception(f"Job {id} stopped")
            elif jobinfo["status"] == "SUCCEEDED":
                return jobinfo
        raise Exception(
            f"Job {id} did not complete in the polling "
             "time (retries: {retries}, poll_wait: {poll_wait})"
        )

    def create_job(self, type: JobType, request: JobCreate) -> JobResponse:
        """Create a new job.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient
                from schemas.jobs import JobType, JobCreate

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.jobs.create_job(JobType.EVALUATION, JobCreate(...))

        Args:
            type(JobType): The kind of job to create. It can be either
                EVALUATION or INFERENCE.
            request(JobCreate): The job's configuration.

        Returns:
            JobResponse: The information for the newly created job.
        """
        response = self.client.get_response(
            f"{self.JOBS_ROUTE}/{type.value}",
            method=HTTPMethod.POST,
            data=request.model_dump_json(),
        )

        if not response:
            return []

        return JobResponse(**(response.json()))

    def get_job_result(self, id: UUID) -> JobResultResponse:
        """Return the results of a specific job.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.jobs.get_job_result(job_id)

        Args:
            id (str): The ID of the job results to retrieve.

        Returns:
            JobResultResponse: The job results for the provided ID.
        """
        response = self.client.get_response(f"{self.JOBS_ROUTE}/{id}")

        if not response:
            return []

        return JobResultResponse(**(response.json()))

    def get_job_download(self, id: UUID) -> JobResultDownloadResponse:
        """Return the download link for the results of a specific job.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.jobs.get_job_download(job_id)

        Args:
            id (str): The ID of the job download link to retrieve.

        Returns:
            JobResultDownloadResponse: The job download link for the provided
                ID.
        """
        response = self.client.get_response(f"{self.JOBS_ROUTE}/{id}/result/download")

        if not response:
            return []

        return JobResultDownloadResponse(**(response.json()))

import time
from typing import Type

import transifex

from .exceptions import DownloadException, UploadException
from .jsonapi import JsonApi
from .jsonapi import Resource as JsonApiResource


class DownloadMixin(object):
    """Mixin that offers a download method for Transifex APIv3."""

    @classmethod
    def download(cls, interval=5, *args, **kwargs):
        """Create and poll an async download. Return the download URL when
        done.
        """

        download = cls.create(*args, **kwargs)
        while True:
            if hasattr(download, "errors") and len(download.errors) > 0:
                # The way Transifex APIv3 works right now, only one error will be
                # returned, so we give priority to the first error's 'detail' field. If
                # more errors are included in the future, the user can inspect the
                # exception's second argument
                raise DownloadException(download.error[0]["detail"], download.errors)
            if download.redirect:
                return download.redirect
            time.sleep(interval)
            download.reload()


class UploadMixin(object):
    @classmethod
    def upload(cls, content, interval=5, **data):
        """Upload content with multipart/form-data.

        :param content: A string or file-like object that will be sent as a
                        file upload
        :param interval: How often (in seconds) to poll for the completion
                         of the upload job
        :param data: Data that will be sent as (non file) form fields
        """
        for key, value in list(data.items()):
            if isinstance(value, JsonApiResource):
                data[key] = value.id

        upload = cls.create_with_form(data=data, files={"content": content})

        while True:
            if hasattr(upload, "errors") and len(upload.errors) > 0:
                # The way Transifex APIv3 works right now, only one error will be
                # returned, so we give priority to the first error's 'detail' field. If
                # more errors are included in the future, the user can inspect the
                # exception's second argument
                raise UploadException(upload.errors[0]["detail"], upload.errors)

            if upload.redirect:
                return upload.follow()
            elif (
                hasattr(upload, "attributes")
                and upload.attributes.get("status") == "succeeded"
            ):
                return upload.attributes.get("details")

            time.sleep(interval)
            upload.reload()


class TransifexApi(JsonApi):
    HOST = "https://rest.api.transifex.com"
    HEADERS = {
        "User-Agent": "Transifex-API-SDK/{}".format(transifex.__version__),
    }

    # Auto-completion support
    Organization: Type[JsonApiResource]
    Team: Type[JsonApiResource]
    Project: Type[JsonApiResource]
    Language: Type[JsonApiResource]
    Resource: Type[JsonApiResource]
    ResourceString: Type[JsonApiResource]
    ResourceTranslation: Type[JsonApiResource]
    ResourceStringsAsyncUpload: Type[JsonApiResource]
    ResourceTranslationsAsyncUpload: Type[JsonApiResource]
    User: Type[JsonApiResource]
    TeamMembership: Type[JsonApiResource]
    ResourceLanguageStats: Type[JsonApiResource]
    ResourceStringsAsyncDownload: Type[JsonApiResource]
    ResourceTranslationsAsyncDownload: Type[JsonApiResource]
    I18nFormat: Type[JsonApiResource]
    ResourceStringsRevision: Type[JsonApiResource]
    ContextScreenshotMap: Type[JsonApiResource]
    ContextScreenshot: Type[JsonApiResource]
    OrganizationActivityReportsAsyncDownload: Type[JsonApiResource]
    ProjectActivityReportsAsyncDownload: Type[JsonApiResource]
    ResourceActivityReportsAsyncDownload: Type[JsonApiResource]
    ProjectWebhook: Type[JsonApiResource]
    ResourceStringComment: Type[JsonApiResource]
    TeamActivityReportsAsyncDownload: Type[JsonApiResource]
    TmxAsyncDownload: Type[JsonApiResource]
    TmxAsyncUpload: Type[JsonApiResource]

    organizations: Type[JsonApiResource]
    teams: Type[JsonApiResource]
    projects: Type[JsonApiResource]
    languages: Type[JsonApiResource]
    resources: Type[JsonApiResource]
    resource_strings: Type[JsonApiResource]
    resource_translations: Type[JsonApiResource]
    resource_strings_async_uploads: Type[JsonApiResource]
    resource_translations_async_uploads: Type[JsonApiResource]
    users: Type[JsonApiResource]
    team_memberships: Type[JsonApiResource]
    resource_language_stats: Type[JsonApiResource]
    resource_strings_async_downloads: Type[JsonApiResource]
    resource_translations_async_downloads: Type[JsonApiResource]
    i18n_formats: Type[JsonApiResource]
    resource_strings_revisions: Type[JsonApiResource]
    context_screenshot_maps: Type[JsonApiResource]
    context_screenshots: Type[JsonApiResource]
    organization_activity_reports_async_downloads: Type[JsonApiResource]
    project_activity_reports_async_downloads: Type[JsonApiResource]
    resource_activity_reports_async_downloads: Type[JsonApiResource]
    project_webhooks: Type[JsonApiResource]
    resource_string_comments: Type[JsonApiResource]
    team_activity_reports_async_downloads: Type[JsonApiResource]
    tmx_async_downloads: Type[JsonApiResource]
    tmx_async_uploads: Type[JsonApiResource]


@TransifexApi.register
class Organization(JsonApiResource):
    TYPE = "organizations"


@TransifexApi.register
class Team(JsonApiResource):
    TYPE = "teams"


@TransifexApi.register
class Project(JsonApiResource):
    TYPE = "projects"


@TransifexApi.register
class Language(JsonApiResource):
    TYPE = "languages"


@TransifexApi.register
class Resource(JsonApiResource):
    TYPE = "resources"

    def purge(self):
        count = 0
        # Instead of filter, if Resource had a plural relationship to
        # ResourceString, we could do `self.fetch('resource_strings')`
        for page in list(self.API.ResourceString.filter(resource=self).all_pages()):
            count += len(page)
            self.API.ResourceString.bulk_delete(page)
        return count


@TransifexApi.register
class ResourceString(JsonApiResource):
    TYPE = "resource_strings"


@TransifexApi.register
class ResourceTranslation(JsonApiResource):
    TYPE = "resource_translations"
    EDITABLE = ["strings", "reviewed", "proofread"]


@TransifexApi.register
class ResourceStringsAsyncUpload(JsonApiResource, UploadMixin):
    TYPE = "resource_strings_async_uploads"


@TransifexApi.register
class ResourceTranslationsAsyncUpload(JsonApiResource, UploadMixin):
    TYPE = "resource_translations_async_uploads"

    @classmethod
    def upload(cls, content, interval=5, **data):
        data.setdefault("file_type", "default")
        return super().upload(content, interval, **data)


@TransifexApi.register
class User(JsonApiResource):
    TYPE = "users"


@TransifexApi.register
class TeamMembership(JsonApiResource):
    TYPE = "team_memberships"


@TransifexApi.register
class ResourceLanguageStats(JsonApiResource):
    TYPE = "resource_language_stats"


@TransifexApi.register
class ResourceStringsAsyncDownload(JsonApiResource, DownloadMixin):
    TYPE = "resource_strings_async_downloads"


@TransifexApi.register
class ResourceTranslationsAsyncDownload(JsonApiResource, DownloadMixin):
    TYPE = "resource_translations_async_downloads"


@TransifexApi.register
class I18nFormat(JsonApiResource):
    TYPE = "i18n_formats"


@TransifexApi.register
class ResourceStringsRevision(JsonApiResource):
    TYPE = "resource_strings_revisions"


@TransifexApi.register
class ContextScreenshotMap(JsonApiResource):
    TYPE = "context_screenshot_maps"


@TransifexApi.register
class ContextScreenshot(JsonApiResource):
    TYPE = "context_screenshots"


@TransifexApi.register
class OrganizationActivityReportsAsyncDownload(JsonApiResource, DownloadMixin):
    TYPE = "organization_activity_reports_async_downloads"


@TransifexApi.register
class ProjectActivityReportsAsyncDownload(JsonApiResource, DownloadMixin):
    TYPE = "project_activity_reports_async_downloads"


@TransifexApi.register
class ResourceActivityReportsAsyncDownload(JsonApiResource, DownloadMixin):
    TYPE = "resource_activity_reports_async_downloads"


@TransifexApi.register
class ProjectWebhook(JsonApiResource):
    TYPE = "project_webhooks"


@TransifexApi.register
class ResourceStringComment(JsonApiResource):
    TYPE = "resource_string_comments"


@TransifexApi.register
class TeamActivityReportsAsyncDownload(JsonApiResource, DownloadMixin):
    TYPE = "team_activity_reports_async_downloads"


@TransifexApi.register
class TmxAsyncDownload(JsonApiResource, DownloadMixin):
    TYPE = "tmx_async_downloads"


@TransifexApi.register
class TmxAsyncUpload(JsonApiResource, UploadMixin):
    TYPE = "tmx_async_uploads"


@TransifexApi.register
class UniqueIdentifier(JsonApiResource, UploadMixin):
    TYPE = "unique_identifiers"


# This is our global object
transifex_api = TransifexApi()

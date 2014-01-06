# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------

from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from feincms.admin.item_editor import FeinCMSInline
from feincms.module.medialibrary.fields import ContentWithMediaFile


class MediaFileContentInline(FeinCMSInline):
    raw_id_fields = ('mediafile',)
    radio_fields = {'type': admin.VERTICAL}


class MediaFileContent(ContentWithMediaFile):
    """
    Rehashed, backwards-incompatible media file content which does not contain
    the problems from v1 anymore.

    Create a media file content as follows::

        from feincms.content.medialibrary.v2 import MediaFileContent
        Page.create_content_type(MediaFileContent, TYPE_CHOICES=(
            ('default', _('Default')),
            ('lightbox', _('Lightbox')),
            ('whatever', _('Whatever')),
            ))

    For a media file of type 'image' and type 'lightbox', the following
    templates are tried in order:

    * content/mediafile/image_lightbox.html
    * content/mediafile/image.html
    * content/mediafile/lightbox.html
    * content/mediafile/default.html

    The context contains ``content`` and ``request`` (if available).
    """

    feincms_item_editor_inline = MediaFileContentInline

    class Meta:
        abstract = True
        verbose_name = _('media file')
        verbose_name_plural = _('media files')

    @classmethod
    def initialize_type(cls, TYPE_CHOICES=None, POSITION_CHOICES=None, SIZE_CHOICES=None, DISPLAY_CHOICES=None, FORMAT_CHOICES=None, CROP_CHOICES=None):
        if TYPE_CHOICES is None:
            raise ImproperlyConfigured('You have to set TYPE_CHOICES when'
                ' creating a %s' % cls.__name__)

        cls.add_to_class('type', models.CharField(_('type'),
            max_length=20, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0]))

        if POSITION_CHOICES:
            cls.add_to_class('position', models.CharField(_('position'),
                max_length=10,
                choices=POSITION_CHOICES,
                default=POSITION_CHOICES[0][0]
                ))#.contribute_to_class(cls, 'position')

        if SIZE_CHOICES:
            cls.add_to_class('size', models.CharField(_('size'),
                max_length=64,
                choices=SIZE_CHOICES,
                default=SIZE_CHOICES[0][0]
                ))

        if DISPLAY_CHOICES:
            cls.add_to_class('display', models.CharField(_('display'),
                max_length=16,
                choices=DISPLAY_CHOICES,
                default=DISPLAY_CHOICES[0][0]
                ))

        if CROP_CHOICES:
            cls.add_to_class('crop', models.CharField(_('crop'),
                max_length=10,
                choices=CROP_CHOICES,
                default=CROP_CHOICES[0][0]
                ))

        if FORMAT_CHOICES:
            cls.add_to_class('format', models.CharField(_('format'),
                max_length=64,
                choices=FORMAT_CHOICES,
                default=FORMAT_CHOICES[0][0]
                ))#.contribute_to_class(cls, 'format')


    def render(self, **kwargs):
        ctx = {'content': self}
        ctx.update(kwargs)
        return render_to_string([
            'content/mediafile/%s_%s.html' % (self.mediafile.type, self.type),
            'content/mediafile/%s.html' % self.mediafile.type,
            'content/mediafile/%s.html' % self.type,
            'content/mediafile/default.html',
            ], ctx, context_instance=kwargs.get('context'))

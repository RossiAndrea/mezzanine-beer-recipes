import datetime
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from mezzanine.conf import settings
from mezzanine.core.models import Orderable
from mezzanine.core.managers import DisplayableManager
from mezzanine.blog.models import BlogPost as MezzanineBlogPost
from mezzanine.utils.timezone import now

from . import fields


class SubclassingQuerySet(QuerySet):

    def __getitem__(self, k):
        result = super(SubclassingQuerySet, self).__getitem__(k)
        if isinstance(result, BlogProxy):
            return result.as_leaf_class()
        else:
            return result

    def __iter__(self):
        for item in super(SubclassingQuerySet, self).__iter__():
            yield item.as_leaf_class()


class BlogManager(DisplayableManager):
    def get_query_set(self):
        return SubclassingQuerySet(self.model)


class BlogProxy(MezzanineBlogPost):
    content_type = models.ForeignKey(ContentType,
                                     editable=False,
                                     null=True)
    modified_date = models.DateTimeField(_("Last Modified"),
                                         blank=True, null=True)

    template_dir = "blog/"
    secondary = BlogManager()

    def save(self, *args, **kwargs):
        self.modified_date = now()
        if not self.content_type:
            ct = ContentType.objects
            ct = ct.get_for_model(self.__class__)
            self.content_type = ct
        super(BlogProxy, self).save(*args, **kwargs)

    def as_leaf_class(self):
        content_type = self.content_type
        model = content_type.model_class()
        if model == BlogProxy:
            return self
        return model.objects.get(id=self.id)

    def _get_next_or_previous_by_publish_date(self, is_next, **kwargs):
        """
        Retrieves next or previous object by publish date. We implement
        our own version instead of Django's so we can hook into the
        published manager and concrete subclasses.
        """
        arg = "publish_date__gt" if is_next else "publish_date__lt"
        order = "publish_date" if is_next else "-publish_date"
        lookup = {arg: self.publish_date}
        concrete_model = self.__class__
        try:
            queryset = concrete_model.secondary.published
        except AttributeError:
            queryset = concrete_model.secondary.all
        try:
            return queryset(**kwargs).filter(**lookup).order_by(order)[0]
        except IndexError:
            pass


class BlogPost(BlogProxy):
    secondary = BlogManager()

    @models.permalink
    def get_absolute_url(self):
        url_name = "blog_post_detail"
        kwargs = {"slug": "%s/%s" % (settings.ARTICLES_SLUG, self.slug)}
        if settings.BLOG_URLS_USE_DATE:
            url_name = "blog_post_detail_date"
            month = str(self.publish_date.month)
            if len(month) == 1:
                month = "0" + month
            day = str(self.publish_date.day)
            if len(day) == 1:
                day = "0" + day
            kwargs.update({"day": day,
                           "month": month,
                           "year": self.publish_date.year, })
        return (url_name, (), kwargs)

    class Meta:
        verbose_name = _("Blog post")
        verbose_name_plural = _("Blog posts")
        ordering = ("-publish_date",)
        app_label = _("Content")


class Ingredient_Type(models.Model):
    type = models.CharField(max_length=50)

    def __unicode__(self):
        return u"%s" % self.type

    class Meta:
        app_label = _("Recipes")
        verbose_name = _("Ingredient Type")
        verbose_name_plural = _("Ingredient Types")


class Recipe_Ingredients(Orderable):
    recipe = models.ForeignKey("Recipe")
    ingredient = models.ForeignKey("Ingredient")
    quantity = models.IntegerField(help_text="(opzionale) Inserire qui il peso"
                                             " in grammi.",
                                   null=True, blank=True)
    measure = models.CharField(max_length=2, choices=fields.MEASURES,
                               null=True, blank=True)
    timing = models.IntegerField(help_text="(opzionale) Inserire qui il "
                                           "momento di inserimento in "
                                           "bollitura in minuti",
                                 null=True, blank=True, default=0)

    class Meta:
        app_label = _("Recipes")


class Ingredient(models.Model):
    """
    Provides ingredient fields for managing recipe content and making
    it searchable.
    """
    ingredient = models.CharField(_("Ingredient"), max_length=100)
    note = models.CharField(_("Note"), max_length=200, blank=True, null=True)
    type = models.ForeignKey(Ingredient_Type)

    def __unicode__(self):
        return u"%s: %s" % (self.type.type.upper(), self.ingredient)

    class Meta:
        verbose_name = _("Ingredient")
        verbose_name_plural = _("Ingredients")
        app_label = _("Recipes")


class Recipe(BlogProxy):
    """
    Implements the recipe type of page with all recipe fields.
    """
    summary = models.TextField(_("Summary"), blank=True, null=True)

    original_gravity = models.IntegerField(max_length=4)
    final_gravity = models.IntegerField(max_length=4)
    ibu_bitter = models.IntegerField(max_length=2)
    color = models.IntegerField(max_length=1, choices=fields.SRM_CHART,
                                help_text="Inserire il valore del colore nella"
                                          " SRM CHART")
    alchol = models.DecimalField(decimal_places=1, max_digits=3)
    liters = models.IntegerField(max_length=3, choices=fields.LITERS,
                                 default=25)

    difficulty = models.IntegerField(_("Difficulty"),
                                     choices=fields.DIFFICULTIES,
                                     blank=True, null=True)
    source = models.URLField(_("Source"), blank=True, null=True,
                             help_text=_("URL of the source recipe"))
    ingredients = models.ManyToManyField(Ingredient,
                                         through="Recipe_Ingredients")

    template_dir = "recipe/"
    secondary = BlogManager()
    search_fields = ("title", "summary", "description",)

    def __unicode__(self):
        return u'%s' % (self.title)

    @models.permalink
    def get_absolute_url(self):
        url_name = "blog_post_detail"
        kwargs = {"slug": "%s/%s" % (settings.RECIPES_SLUG, self.slug)}
        if settings.BLOG_URLS_USE_DATE:
            url_name = "blog_post_detail_date"
            month = str(self.publish_date.month)
            if len(month) == 1:
                month = "0" + month
            day = str(self.publish_date.day)
            if len(day) == 1:
                day = "0" + day
            kwargs.update({"day": day, "month": month,
                           "year": self.publish_date.year, })
        return (url_name, (), kwargs)

    class Meta:
        verbose_name = _("Recipe")
        verbose_name_plural = _("Recipes")
        ordering = ("-publish_date",)
        app_label = _("Recipes")


class Period(models.Model):
    """
    Provides fields for a period of time
    """
    minutes = models.IntegerField(_("minutes"), default=0)

    def __unicode__(self):
        return "%02d:%02d" % str(datetime.timedelta(minutes=
                                 self.minutes)).split(":")[:2]

    class Meta:
        abstract = True


class Mashing(Period):
    """
    Provides working hour fields for cooking a recipe
    """
    recipe = models.OneToOneField("Recipe", verbose_name=_("Recipe"),
                                  related_name="mashing_time")

    class Meta:
        verbose_name = _("maashing")
        verbose_name_plural = verbose_name
        app_label = _("Recipes")


class Boiling(Period):
    """
    Provides cooking time fields for cooking a recipe
    """
    recipe = models.OneToOneField("Recipe", verbose_name=_("Recipe"),
                                  related_name="boiling_time")

    class Meta:
        verbose_name = _("boiling")
        verbose_name_plural = verbose_name
        app_label = _("Recipes")


class Fermentation(models.Model):
    """
    Provides rest time fields for cooking a recipe
    """
    recipe = models.OneToOneField("Recipe", verbose_name=_("Recipe"),
                                  related_name="fermentation_period")
    days = models.IntegerField(_("days"), default=0)

    def __unicode__(self):
        return _("%s days" % self.days)

    class Meta:
        verbose_name = _("fermentation")
        verbose_name_plural = verbose_name
        app_label = _("Recipes")

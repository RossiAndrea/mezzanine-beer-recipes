from django.conf.urls.defaults import patterns, url

from mezzanine.conf import settings
from .models import Recipe

# Recipe patterns.
urlpatterns = patterns("mezzanine_beer_recipes.views",
                       # RECIPE LIST
                       url("^%s/tag/(?P<tag>.*)/$" % settings.RECIPES_SLUG,
                           "recipe_list", name="recipe_list_tag"),
                       url("^%s/category/(?P<category>.*)/$" %
                           settings.RECIPES_SLUG, "recipe_list",
                           name="blog_post_list_category"),
                       url(r'%s/$' % settings.RECIPES_SLUG, 'recipe_list',
                           kwargs=dict(model=Recipe), name="recipe_list"),
                       url("^%s/author/(?P<username>.*)/$" %
                           settings.RECIPES_SLUG,
                           "recipe_list", name="recipe_list_author"),
                       url("^%s/archive/(?P<year>\d{4})/(?P<month>\d{1,2})/$" %
                           settings.RECIPES_SLUG,
                           "recipe_list", name="recipe_list_month"),
                       url("^%s/archive/(?P<year>\d{4})/$" %
                           settings.RECIPES_SLUG,
                           "recipe_list", name="recipe_list_year"),
                       url("^$", "recipe_list", name="recipe_list"),

                       # RECIPE DETAILS
                       url("^%s/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>"
                           "\d{1,2})/(?P<slug>.*)/$" % settings.RECIPES_SLUG,
                           "recipe_detail", name="recipe_detail_day"),
                       url("^%s/(?P<year>\d{4})/(?P<month>\d{1,2})/"
                           "(?P<slug>.*)/$" % settings.RECIPES_SLUG,
                           "recipe_detail", name="recipe_detail_month"),
                       url("^%s/(?P<year>\d{4})/(?P<slug>.*)/$" %
                           settings.RECIPES_SLUG, "recipe_detail",
                           name="recipe_detail_year"),
                       url("^%s/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>"
                           "\d{1,2})/(?P<slug>.*)/$" % settings.RECIPES_SLUG,
                           "recipe_detail", name="recipe_detail_day"),
                       url("^%s/(?P<slug>.*)/$" % settings.RECIPES_SLUG,
                           "recipe_detail", name="recipe_detail"),

                       )

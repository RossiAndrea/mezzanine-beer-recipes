from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from calendar import month_name

from mezzanine.utils.views import render
from mezzanine.blog.models import BlogCategory
from mezzanine.conf import settings
from mezzanine.generic.models import Keyword
from mezzanine.utils.views import paginate

from .models import Recipe


def recipe_list(request, tag=None, year=None, month=None, username=None,
                category=None, template="recipe/recipe_list.html",
                model=Recipe):
    """
    Display a list of recipe that are filtered by tag, year, month,
    author or category. Custom templates are checked for using the name
    ``recipe/recipe_list_XXX.html`` where ``XXX`` is either the
    category slug or author's username if given.
    """
    settings.use_editable()
    templates = []
    recipes = model.objects.published(for_user=request.user)
    if tag is not None:
        tag = get_object_or_404(Keyword, slug=tag)
        recipes = recipes.filter(keywords__in=tag.assignments.all())
    if year is not None:
        recipes = recipes.filter(publish_date__year=year)
        if month is not None:
            recipes = recipes.filter(publish_date__month=month)
            month = month_name[int(month)]
    if category is not None:
        category = get_object_or_404(BlogCategory, slug=category)
        recipes = recipes.filter(categories=category)
        templates.append(u"recipe/recipe_list_%s.html" %
                         unicode(category.slug))
    author = None
    if username is not None:
        author = get_object_or_404(User, username=username)
        recipes = recipes.filter(user=author)
        templates.append(u"recipe/recipe_list_%s.html" % username)

    prefetch = ("categories", "keywords__keyword")
    recipes = recipes.select_related("user").prefetch_related(*prefetch)
    recipes = paginate(recipes, request.GET.get("page", 1),
                       settings.BLOG_POST_PER_PAGE,
                       settings.MAX_PAGING_LINKS)
    context = {"recipes": recipes, "year": year, "month": month,
               "tag": tag, "category": category, "author": author}
    templates.append(template)
    return render(request, templates, context)


def recipe_detail(request, slug, year=None, month=None, day=None,
                  model=Recipe, template="recipe/recipe_detail.html"):
    """
    Custom templates are checked for using the name
    ``blog/blog_post_detail_XXX.html`` where ``XXX`` is the blog
    posts's slug.
    """
    recipes = model.objects.published(for_user=
                                      request.user).select_related()
    recipe = get_object_or_404(recipes, slug=slug)
    context = {"recipe": recipe, "editable_obj": recipe}
    templates = [u"recipe/recipe_detail_%s.html" % unicode(slug), template]
    return render(request, templates, context)

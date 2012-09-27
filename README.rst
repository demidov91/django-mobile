=============
django-mobile-threadsafe
=============

.. _Note!:
This is thread safe version of original *django-mobile* package. Use it if you can't gurantee that **python** part of requests processing  is served by one thread. Or if you like **explicity** of this package. Apache is not thread safe but you can configure it to use one thread for process and problem of original *django-mobile* will be resolved.

:: _Differense between django-mobile-threadsafe and django-mobile
1. It holds only ``TemplateResponse`` responses. Syntax is practically the same as for usual ``render_to_response`` but someone may not like it.
2. You should register separate inclusion tags for mobile version if you want to render other templates with them.
3. You should declare template names in templatetags explicitly. For example, django-mobile uses ``{% extends base.html %}`` and  django-mobile-threadsafe uses ``{% extends mobile/base.html %}``  - that will extend the same mobile/base.html template.
4. Yes, this is thread-safe.


Last thing to remember about is **cashing** - it needs one more middleware and django-mobile's implementation of ``cache_page`` decorator. This is the same as original package have Original package manage it the same way. I've mantioned it only because it influnses on your views, rest of the work is going on in separate template directory.



.. _introduction:

**django-mobile-threadsafe** provides a simple way to detect mobile browsers and gives
you tools at your hand to render some different templates to deliver a mobile
version of your site to the user. 

The idea is to make minor changes in views but to transparently
interchange the templates used to render a response. This is done in two
steps:

1. The request middleware determines the client's preference to view your site. E.g. if
   he wants to use the mobile flavour or the full desktop flavour.
2. The 'template response' middleware takes then care of choosing the correct templates based
   on the flavour detected in the middleware.

**django-mobile-threadsafe** needs your views to return ``TemplateResponse`` objects instead of usual ``HttpResponse`` or shortcut ``render_to_response``. It is easy to change your view to use them::

    t = loader.get_template(template_name)
    c = RequestContext(request, some_dictionary_as_context)
    return HttpResponse(t.render(c))

or::

    return render_to_response(template_name, some_dictionary_as_context, context_instance = RequestContext(request))

becomes::

    return TemplateResponse(request, template_name, some_dictionary_as_context)

* - Oh! But what about cookies?! I can't set them without response object!* 
    - Everything is under control. They are served by ``request.cookies_to_save.add(cookies_dictionary, path='/')`` method with the same middleware as django-mobile.

Installation
============

.. _installation:

*Pre-Requirements:* Default implemetation of ``django_mobile`` depends on django's session framework. So before you try to use ``django_mobile`` make sure that the sessions framework is enabled and working.

1. Make sure that all views that will be used by ``django-mobile`` return objects of ``TemplateResponse`` class declared in ``django.template.response``. 
2. Install ``django_mobile`` with your favourite python tool, e.g. with
   ``easy_install django-mobile-threadsafe`` or ``pip install django-mobile-threadsafe``.
3. Add ``django_mobile.session.SessionMiddleware`` to your
   ``MIDDLEWARE_CLASSES`` setting. Make sure it's listed *after* ``SessionMiddleware``.


Thats all :) Now you should be able to use **django-mobile** in its glory. Read below of how
things work and which settings can be tweaked to modify **django-mobile**'s
behaviour.


Usage
=====

.. _flavours:

The concept of **django-mobile** is build around the ideas of different
*flavours* for your site. For example the *mobile* version is described as
one possible *flavour*, the desktop version as another.

This makes it possible to provide many possible designs instead of just
differentiating between a full desktop experience and one mobile version.  You
can make multiple mobile flavours available e.g. one for mobile safari on the
iPhone and Android as well as one for Opera and an extra one for the internet
tablets like the iPad.

*Note:* By default **django-mobile** only distinguishes between *full* and
*mobile* flavour.

*request* object gets to your views with instansce of **DjangoMobile** class assigned to the ``flavour`` field. You can use this in your views to provide separate logic. It is very usefull to have such methods as request.flavour.**is_mobile**, request.flavour.**is_default** or request.flavour.**get** in your python view. First to methods return boolean value, last one - string, name of the flavour.

This flavour is then use to transparently choose custom templates for this
special flavour. The selected template will have the current flavour prefixed
to the template name you actually want to render. This means when
``TemplateResponse('index.html', ...)`` is called with the *mobile* flavour
being active will actually return a response rendered with the
``mobile/index.html`` template. But if this flavoured template is not
available it will gracefully fallback to the default ``index.html`` template only if you was using HttpResponse object instead of TemplateResponse to render that template. I'll try to make TemplateResponse object work in the same way in the next version. 


Changing the current flavour
----------------------------

The basic use case of **django-mobile** is obviously to serve a mobile version
of your site to users. The selection of the correct flavour is usually already
done in the middlewares when your own views are called. In some cases you want
to change the currently used flavour in your view or somewhere else. You can
do this by simply calling ``django_mobile.set_flavour(flavour)``. The first argument is self explaining. But keep in mind that you only can pass in a flavour that you is also in your ``FLAVOURS``
setting. Otherwise ``set_flavour`` will raise a ``ValueError``. The optional
``permanent`` parameters defines if the change of the flavour is remember for
future requests of the same client.

Your users can set their desired flavour them self. They just need to specify
the ``flavour`` GET parameter on a request to your site. This will permanently
choose this flavour as their preference to view the site.

You can use this GET parameter to let the user select from your available
flavours::

    <ul>
        <li><a href="?flavour=full">Get the full experience</a>
        <li><a href="?flavour=mobile">View our mobile version</a>
        <li><a href="?flavour=ipad">View our iPad version</a>
    </ul>



.. _caching:

Django is shipping with some convenience methods to easily cache your views.
One of them is ``django.views.decorators.cache.cache_page``. The problem with
caching a whole page in conjunction with **django-mobile** is, that django's
caching system is not aware of flavours. This means that if the first request
to a page is served with a mobile flavour, the second request might also
get a page rendered with the mobile flavour from the cache -- even if the
second one was requested by a desktop browser.

**django-mobile** is shipping with it's own implementation of ``cache_page``
to resolve this issue. Please use ``django_mobile.cache.cache_page`` instead
of django's own ``cache_page`` decorator.

You can also use django's caching middlewares
``django.middleware.cache.UpdateCacheMiddleware`` and
``FetchFromCacheMiddleware`` like you already do. But to make them aware of
flavours, you need to add
``django_mobile.cache.middleware.CacheFlavourMiddleware`` as second last item
in the ``MIDDLEWARE_CLASSES`` settings, right before
``FetchFromCacheMiddleware``.


Customization
=============

.. _customization:

There are some points available that let you customize the behaviour of
**django-mobile**. Here are some possibilities listed:


Settings
--------

.. _settings:

Here is a list of settings that are used by **django-mobile** and can be
changed in your own ``settings.py``:

FLAVOURS
^^^^^^^^

A list of available flavours for your site.

**Default:** ``('full', 'mobile')``

DEFAULT_MOBILE_FLAVOUR
^^^^^^^^^^^^^^^^^^^^^^

The flavour which is chosen if the built-in ``MobileDetectionMiddleware``
detects a mobile browser.

**Default:** ``mobile``

FLAVOURS_TEMPLATE_PREFIX
^^^^^^^^^^^^^^^^^^^^^^^^

This string will be prefixed to the template names when searching for
flavoured templates. This is useful if you have many flavours and want to
store them in a common subdirectory.

**Default:** ``''`` (empty string)


FLAVOURS_GET_PARAMETER
^^^^^^^^^^^^^^^^^^^^^^

Users can change the flavour they want to look at with a HTTP GET parameter.
This determines the name of this parameter.  Set it to ``None`` to disable.

**Default:** ``'flavour'``


STATIC_URL_MOBILE
^^^^^^^^^^^^^^^^^

Analog of django's STATIC_URL. It is good practice to use it your template but not necessary. If you was fond of it on desctop version, take an advatage of it in mobile version too. 

**Default:** ``'/media/mobile/'``


FLAVOURS_SESSION_KEY
^^^^^^^^^^^^^^^^^^^^

The user's preference set with the GET parameter is stored in the user's
session by default. This setting determines which session key is used to hold this
information.

**Default:** ``'flavour'``


This is not directly what you want?
=============

*django-mobile-threadsafe* is implemented as Astract factory with django_mobile.Middleware as creater and django_mobile.DjangoMobile as product. Now it has only one implementation, this is in django_mobile.session. You can always write your own.


import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(_('full_name'))

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('role')
        verbose_name_plural = _('roles')

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    creation_date = models.DateTimeField(_('date of film creation'), blank=True)

    rating = models.FloatField(_('rating'), blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)])

    class Type(models.TextChoices):
        MOVIE = 'MV', _('Movie')
        TV_SHOW = 'SH', _('TV Show')

    type = models.CharField(
        max_length=2,
        choices=Type.choices,
        default=Type.MOVIE,
    )

    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('film')
        verbose_name_plural = _('films')

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        unique_together = (('film_work', 'genre'),)


class PersonFilmwork(UUIDMixin):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    role = models.TextField(_('role'), null=False, default='actor')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        unique_together = (('film_work', 'person', 'role'),)

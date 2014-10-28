from django.db import models
from model_utils.managers import InheritanceManager


class Filter(models.Model):
    code = models.CharField(null=False, blank=False, db_index=True, max_length=32, primary_key=True)
    name = models.CharField(null=False, blank=False, max_length=128)
    description = models.TextField(null=True, blank=True)
    priority = models.IntegerField(null=False, default=10)

    objects = InheritanceManager()

    def initial(self):
        return {
            "filter_id": self.code
        }

    @classmethod
    def form_type(cls):
        from frontend.forms import SimpleDbParamForm

        return SimpleDbParamForm

    def append_criteria(self, criteria, get):
        return criteria


class IntRangeFilter(Filter):
    min = models.IntegerField()
    max = models.IntegerField()

    @classmethod
    def form_type(cls):
        from frontend.forms import IntRangeDbParamForm

        return IntRangeDbParamForm

    def append_criteria(self, criteria, get):
        _from = get.get('%s_from' % self.code)
        _to = get.get('%s_to' % self.code)
        if _from:
            criteria = criteria.filter(dbparam__simpledbparam__value__gte=_from,dbparam__filter__code=self.code)
        if _to:
            criteria = criteria.filter(dbparam__simpledbparam__value__lte=_to,dbparam__filter__code=self.code)
        return criteria


class BooleanFilter(Filter):
    def append_criteria(self, criteria, get):
        if get.get(self.code) == 'on':
            return criteria.filter(dbparam__simpledbparam__value__gte=50,dbparam__filter__code=self.code)
        elif get.get(self.code) == 'off':
            return criteria.filter(dbparam__simpledbparam__value__lt=50,dbparam__filter__code=self.code)
        else:
            return criteria


class SelectFilter(Filter):
    required = models.BooleanField(default=False)

    def opts(self):
        return SelectOption.objects.filter(filter=self)

    @classmethod
    def form_type(cls):
        from frontend.forms import SelectDbParamForm

        return SelectDbParamForm


    def initial(self):
        initial_data = {
            "filter_id": self.code
        }
        for option in self.selectoption_set.all():
            initial_data[option.code] = 0
        return initial_data

    def append_criteria(self, criteria, get):
        selected = get.get(self.code)
        for option in self.selectoption_set.all().iterator():
            if selected and option.code in selected:
                criteria = criteria.filter(dbparam__selectdbparam__selectdbparamoption__value__gte=30,
                                           dbparam__selectdbparam__selectdbparamoption__option__code=option.code,
                                           dbparam__filter__code=self.code)
        return criteria


class SelectOption(models.Model):
    filter = models.ForeignKey(SelectFilter)
    code = models.CharField(null=False, blank=False, db_index=True, max_length=32)
    name = models.CharField(null=False, blank=False, max_length=64)


class Db(models.Model):
    name = models.CharField(null=False, blank=False, max_length=64)
    short_description = models.TextField(null=False, blank=False, max_length=512)
    description = models.TextField()
    homepage = models.URLField()

    @property
    def sorted_param_set(self):
        return DbParam.objects.select_subclasses().filter(db_id=self.id).order_by('filter__priority', 'filter__code')


class DbParam(models.Model):
    db = models.ForeignKey(Db, null=False)
    filter = models.ForeignKey(Filter, null=False)
    objects = InheritanceManager()


class SimpleDbParam(DbParam):
    value = models.IntegerField(null=False)


class SelectDbParam(DbParam):
    @property
    def options(self):
        return self.selectdbparamoption_set.all()


class SelectDbParamOption(models.Model):
    param = models.ForeignKey(SelectDbParam, null=False)
    option = models.ForeignKey(SelectOption, null=False)
    value = models.IntegerField(null=False)

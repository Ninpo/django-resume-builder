from django.db import models


class Resume(models.Model):
    """
    Collection of Resumes linked to users.
    """
    user = models.ForeignKey('auth.User')
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title


class ResumeItem(models.Model):
    """
    A single resume item, representing a job and title held over a given period
    of time.
    """
    resume = models.ForeignKey(Resume)

    title = models.CharField(max_length=127)
    company = models.CharField(max_length=127)

    start_date = models.DateField()
    # Null end date indicates position is currently held
    end_date = models.DateField(null=True, blank=True)

    description = models.TextField(max_length=2047, blank=True)

    def __unicode__(self):
        return "{}: {} at {} ({})".format(self.resume.title,
                                          self.title,
                                          self.company,
                                          self.start_date.isoformat())

from django.db import models

class DownloadHistory(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    file_path = models.CharField(max_length=500)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



    class Meta:
        app_label = 'downloader'  # 👈 This forces the model to use the right app

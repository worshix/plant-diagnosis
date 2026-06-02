from django.db import models


class LeafImage(models.Model):
    DISEASE_CHOICES = [
        ('angular_leaf_spot', 'Angular Leaf Spot'),
        ('wildfire', 'Wildfire'),
        ('healthy', 'Healthy'),
        ('unknown', 'Unknown'),
    ]
    
    image = models.ImageField(upload_to='leaf_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Environmental conditions
    temperature = models.FloatField(help_text='Temperature in °C', null=True, blank=True)
    humidity = models.FloatField(help_text='Humidity percentage', null=True, blank=True)
    moisture_content = models.FloatField(help_text='Soil moisture content %', null=True, blank=True)
    
    # Classification (manual or predicted)
    actual_disease = models.CharField(
        max_length=50, 
        choices=DISEASE_CHOICES,
        default='unknown',
        help_text='Actual/known disease label (for training data)'
    )
    predicted_disease = models.CharField(
        max_length=50,
        choices=DISEASE_CHOICES,
        null=True,
        blank=True,
        help_text='AI predicted disease'
    )
    confidence_score = models.FloatField(null=True, blank=True, help_text='Prediction confidence %')
    
    # Notes
    notes = models.TextField(blank=True, help_text='Additional observations')
    
    # Claude AI classification details
    claude_reasoning = models.TextField(blank=True, help_text='AI explanation of classification')
    claude_features = models.TextField(blank=True, help_text='Distinguishing features identified by AI')
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.actual_disease} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

import json
import os
from django.conf import settings
from data.models import Holding

benchmark_holdings = open(os.path.join(settings.BASE_DIR, 'data/fixtures/benchmarkHoldings.json'))
bh = json.loads(benchmark_holdings.read())

for holding in bh:
    fields = holding.get("fields")
    ticker = fields.get("ticker")
    if not Holding.objects.filter(ticker=ticker).exists():
        fields["category"] = "MUTF"
        Holding.objects.create(**fields)
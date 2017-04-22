from data.models import Benchmark


def run():

    benchmark_file_map = {}
    benchmark_names = []
    for i in range(2025, 2065, 5):
        name = "{} Vestivise Target Date Index".format(i)
        benchmark_names.append(name)
        benchmark_file_map[name] = "ms_targ_{}.json".format(str(i))

    group = 60
    for i in range(len(benchmark_names)):
        age_group = group - i * 5
        name = benchmark_names[i]
        b = Benchmark.objects.get(name=name)
        b.age_group = age_group
        b.save()

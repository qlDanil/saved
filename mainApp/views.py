from django.shortcuts import render


def main_window(request):
    return render(request, 'mainApp/main.html', )

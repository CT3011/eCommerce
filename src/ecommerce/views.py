from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from .forms import ContectForm

def home_page(request):
    template_name = "ecommerce/home_page.html"
    context = {"title": "Hello Home Page.",
                "content": "welcome to The Homepage",
               }
    if request.user.is_authenticated:
        context["prium_content"]= "YEAHHHHH"
    return render(request, template_name, context)

def about_page(request):
    template_name = "ecommerce/home_page.html"
    context = {"title": "About Page.",
                "content": "welcome to The About Page"
               }
    return render(request, template_name, context)



def contact_page(request):
    contect_form= ContectForm(request.POST or None)
    if contect_form.is_valid():
        print(contect_form.cleaned_data)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"message":"Thank you form submiting."})
        
    
    if contect_form.errors:
        errors = contect_form.errors.as_json()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse(errors, status=400, content_type='application/json')
        
    template_name = "ecommerce/view.html"
    context = {"title": "Contact Page.",
                "content": "welcome to The Contact Page",
                "form": contect_form,
               }
    # if request.method =="POST":
    #     print(request.POST)
    #     print(request.POST.get("fullname"))
    #     print(request.POST.get("email"))
    #     print(request.POST.get("contect"))
    return render(request, template_name, context)
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from .forms import ResumeForm, ResumeItemForm
from .models import Resume, ResumeItem


@login_required
def resume_list_view(request):
    """
    List the user's resumes
    """
    resumes = Resume.objects.filter(user=request.user).order_by('title').annotate(num_items=Count('resumeitem'))

    return render(request, 'resume/resume_list.html', {'resumes': resumes})


@login_required
def resume_view(request, resume_id):
    """
    Handle a request to view a user's resume.
    """
    resume = Resume.objects.get(pk=resume_id)
    resume_items = ResumeItem.objects\
        .filter(resume=resume.id)\
        .order_by('-start_date')

    template_arguments = {'resume_id': resume.id, 'resume_title': resume.title, 'resume_items': resume_items}

    return render(request, 'resume/resume.html', template_arguments)


@login_required
def resume_item_create_view(request, resume_id):
    """
    Handle a request to create a new resume item.
    """
    resume = Resume.objects.get(pk=resume_id)
    if request.method == 'POST':
        form = ResumeItemForm(request.POST)
        if form.is_valid():
            new_resume_item = form.save(commit=False)
            new_resume_item.resume = resume
            new_resume_item.save()

            return redirect(resume_item_edit_view, new_resume_item.resume_id, new_resume_item.id)
    else:
        form = ResumeItemForm()

    return render(request, 'resume/resume_item_create.html', {'resume_id': resume.id, 'form': form})


@login_required
def resume_create_view(request):
    """
    Create a new resume.

    :return: Redirect to new resume view
    """
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            new_resume = form.save(commit=False)
            new_resume.user = request.user
            new_resume.title = request.POST.get('title')
            new_resume.save()

            return redirect(resume_view, new_resume.id)
        else:
            raise ValueError("Form not valid!")
    else:
        form = ResumeForm()

    return render(request, 'resume/resume_create.html', {'form': form})



@login_required
def resume_item_edit_view(request, resume_id, resume_item_id):
    """
    Handle a request to edit a resume item.

    :param resume_item_id: The database ID of the ResumeItem to edit.
    """
    resume = Resume.objects.get(pk=resume_id)
    try:
        resume_item = ResumeItem.objects\
            .filter(resume=resume.id)\
            .get(id=resume_item_id)
    except ResumeItem.DoesNotExist:
        raise Http404

    template_dict = {'resume_id': resume.id}

    if request.method == 'POST':
        if 'delete' in request.POST:
            resume_item.delete()
            return redirect(resume_view, resume_id)

        form = ResumeItemForm(request.POST, instance=resume_item)
        if form.is_valid():
            form.save()
            form = ResumeItemForm(instance=resume_item)
            template_dict['message'] = 'Resume item updated'
    else:
        form = ResumeItemForm(instance=resume_item)

    template_dict['form'] = form

    return render(request, 'resume/resume_item_edit.html', template_dict)

@login_required
def resume_edit_view(request, resume_id):
    """
    Rename a resume
    :param resume_id: Database ID of the resume to rename.
    :return: redirect back to resume list.
    """
    resume = Resume.objects.get(pk=resume_id)
    template_dict = {'resume': resume}
    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=resume)
        if form.is_valid():
            form.save()
            form = ResumeForm(instance=resume)
            template_dict['message'] = 'Resume updated'
            return redirect(resume_list_view)
    else:
        form = ResumeForm(instance=resume)

    template_dict['form'] = form

    return render(request, 'resume/resume_edit.html', template_dict)
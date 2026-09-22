from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .models import Mentorados, Navigators, DisponibilidadedeHorarios, Reuniao, Tarefa, Upload
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta
from .auth import valida_token
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
def mentorados(request):  
    if request.method == 'GET':
        navigators = Navigators.objects.filter(user=request.user)
        mentorados = Mentorados.objects.filter(user=request.user)
        
        estagios_flat = []
        qtd_estagios = []
        for i in Mentorados.estagio_choices:
            estagios_flat.append(i[1])
        
        for i, j in Mentorados.estagio_choices:
            x = Mentorados.objects.filter(estagio=i).filter(user=request.user).count()
            qtd_estagios.append(x)
        
        return render(request, 'mentorados.html', {'estagios': Mentorados.estagio_choices, 'navigators': navigators, 'mentorados':mentorados, 'estagios_flat':estagios_flat, 'qtd_estagios':qtd_estagios})
    
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        foto = request.FILES.get('foto')
        estagio = request.POST.get("estagio")
        navigator = request.POST.get('navigator')
        if not navigator:
            navigator = None
        
        mentorado = Mentorados(
            nome=nome,
            foto=foto,
            estagio=estagio,
            navigator_id=navigator,
            user=request.user
        )

        mentorado.save()
        
        messages.add_message(request, constants.SUCCESS, 'Mentorado cadastrado com sucesso.')
        return redirect('mentorados')

@login_required
def cadastrar_navigator(request):
    if request.method == 'POST':
        nome = request.POST.get('nome_navigator')
        if nome and nome.strip():
            navigator = Navigators(
                nome=nome.strip(),
                user=request.user
            )
            navigator.save()
            messages.add_message(request, constants.SUCCESS, 'Navigator cadastrado com sucesso.')
        else:
            messages.add_message(request, constants.ERROR, 'Informe o nome do Navigator.')
    return redirect('mentorados')

@login_required    
def reunioes(request):
    if request.method == 'GET':
        reunioes = Reuniao.objects.filter(data__mentor=request.user)
        disponibilidades = DisponibilidadedeHorarios.objects.filter(
            mentor=request.user,
            agendado=False
        ).order_by('data_inicial')
        return render(request, 'reunioes.html', {
            'reunioes': reunioes,
            'disponibilidades': disponibilidades
        })
    elif request.method =='POST':
        data = request.POST.get('data')
        data = datetime.strptime(data, '%Y-%m-%dT%H:%M')
        
        # Impede horários sobrepostos ou com menos de uma hora de intervalo.
        disponibilidades = DisponibilidadedeHorarios.objects.filter(mentor=request.user).filter(
            data_inicial__gte = (data - timedelta(minutes=60)),
            data_inicial__lte = (data + timedelta(minutes=60))
        )

        if disponibilidades.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um horário dentro do intervalo de uma hora antes ou depois.')
            return redirect('reunioes')
        
        disponibilidades = DisponibilidadedeHorarios(
            data_inicial = data,
            mentor = request.user,            
        )
        
        disponibilidades.save()
        
        messages.add_message(request, constants.SUCCESS, 'Horário disponibilizado com sucesso!')
        return redirect('reunioes')
    
def auth(request):
    if request.method == 'GET':
        return render(request, 'auth_mentorado.html')
    
    elif request.method =='POST':
        token = request.POST.get('token')
        
        if not Mentorados.objects.filter(token=token).exists():
            messages.add_message(request, constants.ERROR, 'Token inválido')
            return redirect('auth_mentorado')
        
        response = redirect('escolher_dia')
        response.set_cookie('auth_token', token, max_age=3600)
        
        return response

def escolher_dia(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
    
    if request.method == 'GET':
        mentorado = valida_token(request.COOKIES.get('auth_token'))
        
        disponibilidades = DisponibilidadedeHorarios.objects.filter(
            data_inicial__gte=datetime.now(),
            agendado=False,
            mentor=mentorado.user
        ).values_list('data_inicial', flat=True)
        
        
        dias_da_semana={
            0: 'Segunda-feira',
            1: 'Terça-feira',
            2: 'Quarta-feira',
            3: 'Quinta-feira',
            4: 'Sexta-feira',
            5: 'Sábado',
            6: 'Domingo',
        }
        
        meses_do_ano = {
            1: 'Janeiro',
            2: 'Fevereiro',
            3: 'Março',
            4: 'Abril',
            5: 'Maio',
            6: 'Junho',
            7: 'Julho',
            8: 'Agosto',
            9: 'Setembro',
            10: 'Outubro',
            11: 'Novembro',
            12: 'Dezembro'
        }
        
        datas = []
        
        for i in disponibilidades:
            data=i.date()
            datas.append({
                'horario': i.date().strftime('%d-%m-%Y'),
                'dia': dias_da_semana[data.weekday()],
                'mes': meses_do_ano[int(data.strftime('%m'))]
                })
        
        
        return render(request, 'escolher_dia.html', {
            'horarios': [dict(t) for t in {tuple(d.items()) for d in datas}]
        })

def agendar_reuniao(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
    
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    
    #Valida se o horario agendado é realmente de um mentor do mentorado
    
    if request.method=='GET':
        data = request.GET.get('data')
        data = datetime.strptime(data, '%d-%m-%Y')
        
        horarios = DisponibilidadedeHorarios.objects.filter(
            data_inicial__gte=data,
            data_inicial__lt=data + timedelta(days=1),
            agendado=False,
            mentor=mentorado.user
        )
        return render(request, 'agendar_reuniao.html', {'horarios':horarios, 'tags':Reuniao.tag_choices})
    
    else:
        horario_id = request.POST.get('horario')
        tag = request.POST.get('tag')
        descricao = request.POST.get('descricao')

        horario = DisponibilidadedeHorarios.objects.filter(
            id=horario_id,
            mentor=mentorado.user,
            agendado=False
        ).first()
        if not horario:
            messages.add_message(request, constants.ERROR, 'Esse horário não está mais disponível.')
            return redirect('escolher_dia')
        
        #Atomicidade
        
        reuniao = Reuniao(
            data=horario,
            mentorado=mentorado,
            tag=tag,
            descricao=descricao
        )
        reuniao.save()
        
        horario.agendado = True
        horario.save()
        
        messages.add_message(request, constants.SUCCESS, 'Reunião Agendada com sucesso.')
        return redirect('escolher_dia')

@login_required    
def tarefa(request, id):
    mentorado = Mentorados.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404
    
    if request.method == 'GET':
        tarefas = Tarefa.objects.filter(mentorado=mentorado)
        videos = Upload.objects.filter(mentorado=mentorado)
        return render(request, 'tarefa.html', {'mentorado': mentorado, 'tarefas': tarefas, 'videos':videos})
    else:
        tarefa = request.POST.get('tarefa')
        t = Tarefa(
            mentorado = mentorado,
            tarefa=tarefa
        )
        t.save()
        return redirect(f'/mentorados/tarefa/{mentorado.id}')

@login_required    
def upload(request, id):
    mentorado = Mentorados.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404
    
    video = request.FILES.get('video')
    upload = Upload(
        mentorado=mentorado,
        video=video
    )
    upload.save()
    return redirect(f'/mentorados/tarefa/{mentorado.id}')

def tarefa_mentorado(request):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('auth_mentorado')
    
    if request.method == 'GET':
        videos = Upload.objects.filter(mentorado=mentorado)
        tarefas = Tarefa.objects.filter(mentorado=mentorado)
        return render(request, 'tarefa_mentorado.html', {'mentorado':mentorado, 'videos':videos, 'tarefas':tarefas})


@csrf_exempt    
def tarefa_alterar(request, id):
    tarefa = Tarefa.objects.get(id=id)
    
    tarefa.realizada = not tarefa.realizada
    tarefa.save()
    
    print(id)
    return HttpResponse('Teste')

def not_found(request, exception):
    return render(request, 'not_found.html', status=404)
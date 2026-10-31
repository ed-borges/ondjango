# Testar a fase 2 sem VPS

É possível experimentar o Judge0 no próprio computador sem pagar uma VPS: criar uma **máquina virtual (VM) Linux dedicada**, instalar Docker dentro dela e tratá-la como um servidor de testes descartável. Docker cria contentores; não substitui, por si só, a VM nem cria uma fronteira segura para código desconhecido.

Para instruções específicas do Linux Mint, consulta [linux-mint-vm.md](linux-mint-vm.md). Esta é uma proposta de ambiente local. Nesta sessão não temos Docker nem uma VM, por isso **não executámos o Judge0 nem validámos os cinco runtimes reais**. O Lab da Ondjango continua desativado por defeito.

## 1. Criar a VM

- Utilizar uma solução de virtualização compatível com o teu sistema, por exemplo VirtualBox, e uma imagem Linux obtida de uma fonte oficial. Verificar requisitos do hipervisor e suporte à virtualização no computador.
- Criar uma VM apenas para testes, sem contas, ficheiros ou credenciais reais. Usar NAT para instalar pacotes e descarregar imagens; não usar rede em ponte nem publicar portas na rede local. Desativar pastas partilhadas e outras integrações desnecessárias com o computador anfitrião. Confirmar estas opções no hipervisor escolhido.
- Instalar Docker Engine, o plugin Docker Compose e Python 3 **dentro da VM**. Verificar os requisitos de Linux/cgroups da release do Judge0 antes de alterar configurações do sistema. A compatibilidade varia conforme o hipervisor e os recursos disponíveis.
- Depois de descarregar as imagens, considerar desligar a rede da VM durante os testes. Fazer uma captura/snapshot da VM é útil para a restaurar; não garante isolamento nem substitui a revisão de segurança.

A configuração do Judge0 usa contentores privilegiados: só executar na VM dedicada e com dados e programas de teste controlados. Não usar o mesmo servidor ou contentor da aplicação para executar código de alunos.

## 2. Preparar e iniciar o Judge0

Copiar a pasta `infra/judge0` para a VM e seguir o respetivo [guia de instalação](../infra/judge0/README.md), incluindo revisão das imagens, configuração local de segredos, verificação da configuração e arranque com Compose. O serviço de referência escuta apenas em `127.0.0.1:2358` **dentro da VM**. Não expor essa porta publicamente. Não partilhar `judge0.conf`, logs, `docker inspect` ou tokens.

## 3. Verificar os cinco runtimes localmente

Depois de o Judge0 estar pronto e **apenas dentro da VM**, executar na pasta `infra/judge0`:

```sh
python3 smoke_test.py --confirm-vm
```

O teste contacta apenas `http://127.0.0.1:2358`, confirma que um pedido sem autenticação é recusado, compara IDs com os nomes das linguagens e envia programas fixos e controlados para Python, JavaScript, Java, C# e Ruby. Também verifica que uma resposta incorreta é rejeitada. Os IDs padrão são apenas uma referência; se não corresponderem à instalação, configurar `LAB_LANGUAGE_IDS` como JSON com os IDs verificados antes de repetir o teste. Verificar manualmente as versões: o teste automático só valida os nomes.

O resultado indica **funcionamento básico**, não comprova segurança. Falhas podem significar que o serviço ainda está a iniciar, que um ID/versão difere ou que os limites são insuficientes. Java e C#, por exemplo, podem necessitar de uma revisão cuidadosa dos limites; não os aumentar sem avaliar as consequências.

## 4. Ligar a Ondjango posteriormente

Este teste local **não liga o Django ao Judge0** e não testa o percurso completo no navegador. O adaptador da Ondjango exige uma URL HTTPS e autenticação. Para testar a integração real será preciso preparar um canal privado com TLS válido e restrições de acesso entre a aplicação e a VM, sem expor o serviço à internet, e depois seguir o procedimento `verify_lab` no [guia do Judge0](../infra/judge0/README.md). Não enfraquecer a configuração para usar HTTP remoto.

Só depois de testes de isolamento, bloqueio de rede, limites, fuga, concorrência e abuso numa infraestrutura adequada poderemos considerar ativar submissões de alunos. Consultar a [aceitação da fase 2](aceitacao-fase-2.md); a fase 1 também mantém validação humana pendente.

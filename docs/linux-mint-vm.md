# Preparar uma VM de testes no Linux Mint

Este guia é para testar o Judge0 localmente, sem contratar uma VPS. A VM é separada do Linux Mint anfitrião, mas **não garante isolamento absoluto**. Não usar dados reais nem aceitar código de alunos neste ambiente.

## 1. Instalar um virtualizador no Mint

Uma opção é o VirtualBox disponível nos repositórios da tua versão do Mint:

```sh
sudo apt update
sudo apt install virtualbox
```

Se o pacote não estiver disponível, verifica as instruções da tua versão do Mint. A virtualização por hardware pode precisar de estar ativada na BIOS/UEFI; em algumas máquinas o Secure Boot também pode exigir passos adicionais para os módulos do VirtualBox. Não alteres estas definições sem consultar as instruções do teu equipamento.

## 2. Criar uma VM Linux dedicada

1. Descarrega uma imagem oficial de Ubuntu Server 22.04 LTS em <https://releases.ubuntu.com/22.04/> e verifica a integridade conforme as instruções oficiais. Esta é a versão de referência indicada pela release do Judge0; confirma as atualizações e compatibilidade antes de a instalar.
2. No VirtualBox, cria uma nova VM Linux, com disco virtual próprio. Como ponto de partida para experimentação, podes tentar **2 CPUs, 4 GB de RAM e 25 GB de disco**, desde que o computador anfitrião tenha recursos suficientes. As necessidades reais dependem das imagens e linguagens; não atribuas mais memória do que o Mint pode dispensar.
3. Nas definições de rede, usa **NAT**, sem regras de encaminhamento de portas. Não uses modo ponte. Desativa pastas partilhadas, clipboard partilhado e outras integrações desnecessárias. Não coloques ficheiros pessoais, dados de alunos ou credenciais de produção na VM.
4. Instala o Ubuntu Server e aplica as atualizações de segurança. O Judge0 upstream menciona requisitos de cgroups para Ubuntu 22.04: consulta a [release oficial](https://github.com/judge0/judge0/releases/tag/v1.13.1) e valida a compatibilidade **dentro da VM** antes de alterar o GRUB. Nunca apliques essas alterações ao Mint anfitrião por causa deste teste.

A VM precisa de acesso à internet temporariamente para instalar pacotes e descarregar imagens. Depois podes desligar a sua rede para testes controlados; isto não prova que o sandbox do Judge0 impede acesso à rede.

## 3. Instalar Docker dentro da VM

Segue as [instruções oficiais do Docker Engine para Ubuntu](https://docs.docker.com/engine/install/ubuntu/) dentro da VM, incluindo o plugin Docker Compose. Confirma a instalação com:

```sh
sudo docker --version
sudo docker compose version
python3 --version
```

O acesso ao Docker é privilegiado. Neste guia usamos `sudo` em vez de conceder ao utilizador acesso permanente ao grupo `docker`.

## 4. Preparar o Judge0

Copia para a VM a pasta `infra/judge0` deste projeto, incluindo o guia e os scripts. Se fores obtê-la pelo GitHub, certifica-te de que as alterações mais recentes foram primeiro publicadas na branch ou integradas; os ficheiros que existem apenas nesta sessão ainda não estarão no clone.

Dentro da VM, abre um terminal na pasta `infra/judge0` e segue a secção “Preparar numa VM de teste” do [guia do Judge0](../infra/judge0/README.md). Para os comandos Compose, usa `sudo ./compose.sh` caso o teu utilizador não tenha acesso ao Docker. Cria e guarda `judge0.conf` apenas dentro da VM; **não partilhes o ficheiro, os tokens, os logs ou saídas de inspeção**.

A configuração é uma referência ainda não testada com Docker nesta sessão. Os seus contentores são privilegiados; revê imagens, versões e riscos antes de iniciar. O serviço escuta apenas no loopback da VM. Não cries um encaminhamento público para a porta 2358.

## 5. Executar o teste local controlado

Depois de o Judge0 ter iniciado, na mesma pasta da VM:

```sh
python3 smoke_test.py --confirm-vm
```

O script usa programas fixos e testa autenticação, identificação de Python, JavaScript, Java, C# e Ruby e um caso de resposta incorreta. Não imprime o token. Se houver erro, partilha apenas a mensagem genérica, **sem enviar segredos, ficheiros de configuração ou logs completos**.

Este teste **não prova que a sandbox é segura** e ainda não liga a aplicação Django ao Judge0. A ligação completa precisa de TLS privado e validação adicional, como explicado em [teste local da fase 2](teste-local-fase2.md). O Lab deve permanecer desligado para alunos até concluirmos a revisão de segurança.

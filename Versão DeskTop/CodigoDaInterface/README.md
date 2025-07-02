# MediaFlow Desktop

## 📱 Sobre o MediaFlow Desktop

O MediaFlow Desktop é uma versão nativa do MediaFlow para Windows, oferecendo uma experiência mais rápida e eficiente para download de mídia do YouTube e outras plataformas.

## ✨ Recursos

- **Interface Nativa**: Interface moderna e responsiva com tema escuro/claro
- **Downloads Rápidos**: Processamento otimizado e downloads em paralelo
- **Sem Limitações**: Funciona offline e sem restrições de navegador
- **Múltiplos Formatos**: Suporte completo para vídeo e áudio em diversos formatos
- **Portátil**: Não requer instalação, executável independente

## 🖥️ Requisitos do Sistema

- **Sistema Operacional**: Windows 10 ou superior
- **Arquitetura**: x64 (64 bits)
- **Memória RAM**: Mínimo 4GB recomendado
- **Espaço em Disco**: 100MB livres
- **Conexão**: Internet para downloads

## 🚀 **Build Otimizado - Reduz Detecções de Vírus**

Este projeto inclui otimizações especiais para reduzir falsos positivos de antivírus e firewall.

### 📦 **Como Fazer o Build**

#### **Opção 1: Script Automatizado (Recomendado)**
```bash
# No Windows, execute:
build.bat

# No Linux/Mac, execute:
python build_app.py
```

#### **Opção 2: Manual**
```bash
# Instale as dependências
pip install -r requisitos.txt

# Execute o build
python build_app.py
```

### 🎯 **Onde o App é Gerado**

O app será gerado na pasta `MediaFlow/` (não mais na pasta `dist/`)

### 🛡️ **Otimizações de Segurança Implementadas**

- ✅ **UPX desabilitado** - Reduz detecções de vírus
- ✅ **Informações de versão** - Adiciona metadados legítimos
- ✅ **Manifesto Windows** - Define permissões corretas
- ✅ **Verificação de integridade** - Valida o app
- ✅ **Exclusão de módulos desnecessários** - Reduz tamanho e suspeitas
- ✅ **Delay de inicialização** - Evita detecções automáticas

### 🔧 **Arquivos de Build**

- `build_app.py` - Script principal de build
- `build_config.py` - Configurações de build
- `build.bat` - Script automatizado para Windows
- `app.spec` - Configuração PyInstaller (atualizada)

### 💡 **Dicas para Usuários**

Se o antivírus ainda detectar o app como suspeito:

1. **Adicione como exceção** no seu antivírus
2. **Execute como administrador** se necessário
3. **Verifique a assinatura digital** (se disponível)
4. **Use o app em modo sandbox** para testes

## 📦 Instalação

### Método 1: Download Direto
1. Baixe o arquivo `MediaFlow.exe` da seção de download
2. Execute o arquivo diretamente (não requer instalação)
3. O aplicativo está pronto para uso!

### Método 2: Desenvolvimento
Se você quiser compilar o aplicativo:

```bash
# Instalar dependências
pip install -r requisitos.txt

# Executar o aplicativo
python src/interface.py

# Compilar com PyInstaller (método antigo)
pyinstaller app.spec
```

## 🚀 Como Usar

1. **Inicie o MediaFlow Desktop**
2. **Cole a URL** do vídeo ou música que deseja baixar
3. **Selecione o tipo** de mídia (Vídeo ou Música)
4. **Escolha a qualidade** e formato desejados
5. **Clique em "Baixar Agora"**
6. **Aguarde** o download ser concluído

## 📁 Estrutura do Projeto

```
MediaFlow/
├── src/
│   ├── interface.py          # Interface principal
│   └── recursos/
│       ├── ffmpeg.exe        # FFmpeg para conversão
│       └── icone.ico         # Ícone do aplicativo
├── dist/
│   └── MediaFlow/
│       ├── MediaFlow.exe     # Executável final
│       └── _internal/        # Dependências empacotadas
├── build/                    # Arquivos de build
├── app.spec                  # Configuração do PyInstaller
└── requisitos.txt           # Dependências Python
```

## 🔧 Tecnologias Utilizadas

- **Python 3.13**: Linguagem principal
- **CustomTkinter**: Interface gráfica moderna
- **yt-dlp**: Biblioteca para download de mídia
- **FFmpeg**: Conversão e processamento de áudio/vídeo
- **PyInstaller**: Empacotamento do executável

## 🐛 Solução de Problemas

### Erro: "FFmpeg não encontrado"
- Certifique-se de que o arquivo `ffmpeg.exe` está na pasta `recursos/`
- O aplicativo inclui o FFmpeg empacotado, não é necessário instalar separadamente

### Erro: "Não foi possível obter dados da URL"
- Verifique se a URL é válida
- Certifique-se de que tem conexão com a internet
- Algumas URLs podem estar protegidas ou indisponíveis

### Erro: "Permissão negada"
- Execute o aplicativo como administrador
- Verifique se o antivírus não está bloqueando o aplicativo

## 📝 Changelog

### v1.0
- Interface nativa com CustomTkinter
- Suporte a vídeo e áudio
- Múltiplas resoluções e formatos
- Tema escuro/claro
- Downloads com progresso em tempo real

## 🤝 Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Suporte

Se você encontrar algum problema ou tiver sugestões:

- Abra uma issue no GitHub
- Entre em contato através do email de suporte
- Consulte a documentação online

---

**MediaFlow Desktop** - Baixador de Mídia Avançado para Windows 
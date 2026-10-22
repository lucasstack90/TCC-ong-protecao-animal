# PAWSAFE — Dashboard + Módulo de Animais

Projeto integrado em HTML, CSS, JavaScript e Bootstrap 5, mantendo a estrutura de pastas acordada.

## Estrutura incluída

```text
PAWSAFE/
├── CSS/
│   ├── style.css       # estilos do dashboard
│   └── animais.css     # estilos isolados do módulo de animais
├── Img/
├── js/
│   ├── dashboard.js
│   └── animais.js
├── Pages/
│   └── animais.html
└── index.html
```

## Executar

Abra a pasta no VS Code e execute `index.html` com Live Server. Clique em **Animais** no menu lateral para abrir `Pages/animais.html`.

## Módulo de animais

Inclui busca, filtros por status e espécie, cartões/lista, cadastro e edição, seleção de foto do computador, ficha do animal, vacinas, histórico médico e pesagens. Os dados do módulo são armazenados no `localStorage` do navegador para o protótipo.

## Importante ao mesclar com o projeto local completo

O ZIP de origem disponível nesta conversa continha o dashboard (`index.html`, CSS e `dashboard.js`) e o módulo de animais. As outras páginas que aparecem na estrutura local (`adocoes.html`, `adotantes.html`, `doacoes.html`, `estoque.html`, `Pg_Login.html`, `resgates.html` e `voluntarios.html`) não estavam incluídas no ZIP de origem, portanto não foram substituídas nem recriadas aqui. Ao copiar estes arquivos para o seu projeto completo, mantenha as páginas que já existem dentro de `Pages/`.

O `CSS/animais.css` fica separado do `CSS/style.css` para impedir que os estilos do módulo alterem a aparência do dashboard.


## Navegação lateral compartilhada

A barra lateral é renderizada por `js/sidebar.js` e estilizada por `CSS/sidebar.css`. O mesmo componente foi conectado ao Dashboard (`index.html`) e ao módulo de Animais (`Pages/animais.html`), com o item da página atual destacado automaticamente. Para manter a uniformidade nas demais páginas do sistema, inclua `../CSS/sidebar.css` no `<head>`, substitua a barra lateral antiga por `<div id="sidebarMount"></div>`, use o botão mobile com `id="menuToggle"` e inclua `<script src="../js/sidebar.js"></script>` antes do JavaScript específico da página. As páginas adicionais devem ficar na pasta `Pages/`.

" .vimrc - nothing special here.
syntax on
set ai
set background=light
set bs=2
set expandtab
set fo-=c
set fo-=o
set fo-=r
set history=500
set hlsearch
set noic
set nowrap
set nu
set rnu
set cursorline
set ruler
set splitright
set sts=4
set sw=4
set tabstop=4
color blue
highlight Directory ctermfg=lightcyan

highlight LineNr ctermfg=lightgreen
highlight LineNr ctermbg=black
highlight CursorLine ctermbg=blue ctermfg=white

" Pathogen support:
" execute pathogen#infect()

autocmd VimEnter * if len($TERM)| NERDTree | set nu |endif
autocmd VimEnter * if len($TERM) && argc()|wincmd l|endif


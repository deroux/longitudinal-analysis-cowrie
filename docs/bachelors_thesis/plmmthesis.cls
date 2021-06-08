%%
%% This is file `plmmthesis.cls',
%% generated with the docstrip utility.
%%
%% The original source files were:
%%
%% PLMLaTeX.dtx  (with options: `plmm')
%%
%% \CheckSum{788}
%% \CharacterTable
%%  {Upper-case    \A\B\C\D\E\F\G\H\I\J\K\L\M\N\O\P\Q\R\S\T\U\V\W\X\Y\Z
%%   Lower-case    \a\b\c\d\e\f\g\h\i\j\k\l\m\n\o\p\q\r\s\t\u\v\w\x\y\z
%%   Digits        \0\1\2\3\4\5\6\7\8\9
%%   Exclamation   \!     Double quote  \"     Hash (number) \#
%%   Dollar        \$     Percent       \%     Ampersand     \&
%%   Acute accent  \'     Left paren    \(     Right paren   \)
%%   Asterisk      \*     Plus          \+     Comma         \,
%%   Minus         \-     Point         \.     Solidus       \/
%%   Colon         \:     Semicolon     \;     Less than     \<
%%   Equals        \=     Greater than  \>     Question mark \?
%%   Commercial at \@     Left bracket  \[     Backslash     \\
%%   Right bracket \]     Circumflex    \^     Underscore    \_
%%   Grave accent  \`     Left brace    \{     Vertical bar  \|
%%   Right brace   \}     Tilde         \~}
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{plmmthesis}[2007/06/25 PLM master theses document class]
\newif\if@mainmatter\@mainmattertrue
\LoadClass[a4paper,11pt,abstract=true,twoside,numbers=noendperiod]{scrreprt}
\RequirePackage{fancyhdr}
\RequirePackage[english,ngerman]{babel}
\RequirePackage[round]{natbib}
\RequirePackage{graphicx}
\RequirePackage{geometry}
\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{amsthm}
\RequirePackage{lmodern}
\RequirePackage{microtype}
\RequirePackage{iflang}
\RequirePackage[%
 bookmarks,%
 plainpages=false,%
 pdfpagelabels,%
 colorlinks=false,%
 pdfborder={0 0 0},%
]{hyperref}
\DeclareOption{english}{\AtBeginDocument{\selectlanguage{english}}}
\DeclareOption{german}{\AtBeginDocument{\selectlanguage{ngerman}}}
\ExecuteOptions{english}
\ProcessOptions\relax
\AtBeginDocument{%
 \newcommand{\degree}[1]{\renewcommand{\degreename}{#1}}
 \global\newbox\absbox%
 \renewcommand\abstractname{%
  \IfLanguageName{english}{Abstract}{Zusammenfassung (Englisch)}%
 }
 \newcommand\examplename{%
  \IfLanguageName{english}{Example}{Beispiel}%
 }
 \newcommand\exercisename{%
   \IfLanguageName{english}{Exercise}{Aufgabe}%
 }
 \newcommand\ackname{%
  \IfLanguageName{english}{Acknowledgments}{Danksagung}%
 }
 \definetoday
}
\newcommand\definetoday{%
 \renewcommand*\today{%
  \IfLanguageName{english}{%
   \number\day\space \ifcase\month\or%
    January\or%
    February\or%
    March\or%
    April\or%
    May\or%
    June\or%
    July\or%
    August\or%
    September\or%
    October\or%
    November\or%
    December\or%
   \fi\space \number\year
  }{%
   \number\day.~\ifcase\month\or%
    J\"anner\or%
    Februar\or%
    M\"arz\or%
    April\or%
    Mai\or%
    Juni\or%
    Juli\or%
    August\or%
    September\or%
    Oktober\or%
    November\or%
    Dezember%
   \fi\space \number\year
  }%
 }
}
\AtEndDocument{%
  \cleardoublepage
 \chapter*{Eidesstattliche Erkl{\"a}rung}
 \thispagestyle{empty}

 Ich erkl{\"a}re hiermit an Eides statt durch meine eigenh{\"a}ndige Unterschrift,
 dass ich die vorliegende Arbeit selbst{\"a}ndig verfasst und keine anderen
 als die ange\-gebenen Quellen und Hilfsmittel verwendet habe. Alle Stellen,
 die w{\"o}rtlich oder inhaltlich den angegebenen Quellen entnommen wurden,
 sind als solche kenntlich gemacht.

 \noindent
 %<*plmb>
 Ich erkl{\"a}re mich mit der Archivierung der vorliegenden
 \foreignlanguage{ngerman}{\kindname}
 einverstanden.
 %</plmb>
 %<*plmm|plmp>
 Die vorliegende Arbeit wurde bisher in gleicher oder {\"a}hnlicher Form noch
 nicht als Bachelorarbeit eingereicht.
 %</plmm|plmp>

 \vspace{2cm}

 \noindent\mbox{}
   \hskip 0pt plus .25fill
   \hrulefill
   \hskip 0pt plus .5fill
   \hrulefill
   \hskip 0pt plus .25fill
 \mbox{}
 \\
 \noindent\mbox{}
   \hskip 0pt plus .25fill
   Datum
   \hskip 0pt plus .5fill
   Unterschrift
   \hskip 0pt plus .25fill
 \mbox{}
 \restoregeometry
 \cleardoublepage
}
\let\@OLDappendix\appendix
\renewcommand\appendix{%
\backmatter
\phantomsection{\addcontentsline{toc}{chapter}{\bibname}}
 \bibliographystyle{plainnat}
 \bibliography{\@bibfile}
 \@OLDappendix
 \cleardoublepage

}
\theoremstyle{plain}
\newtheorem{corollary}{Corollary}[%
chapter%
]
\newtheorem{lemma}[corollary]{Lemma}
\newtheorem{proposition}[corollary]{Proposition}
\newtheorem{theorem}[corollary]{Theorem}

\theoremstyle{definition}
\newtheorem{definition}[corollary]{Definition}
\newtheorem{example}[corollary]{\examplename}
\newtheorem{exercise}[corollary]{\exercisename}
\newcommand\@bibfile{biblio}
\newcommand\bibfile[1]{\renewcommand\@bibfile{#1}}
\newcommand*\@supervisor{insert the name of your supervisor}
\global\let\@supervisors\@empty
\newcommand*\@institute{insert the institute of your supervisor}
\newcommand*\institute[1]{\gdef\@institute{#1}}
\newcommand*\@mailaddress\@empty
\global\let\@matriculationnumber\@empty
\newcommand*\mailaddress[1]{\gdef\@mailaddress{#1}}
\newcommand*\matriculationnumber[1]{\gdef\@matriculationnumber{#1}}
\newcommand*\@plaintitle\@empty
\newcommand*\@plainauthor\@empty
\newcommand*\plaintitle[1]{\gdef\@plaintitle{#1}}
\newcommand*\plainauthor[1]{\gdef\@plainauthor{#1}}
\newcommand\kindname{%
 \IfLanguageName{english}{Bachelor~Thesis}{Bachelorarbeit}%
}
\newcommand\supervisorname{%
 \IfLanguageName{english}{Supervisor}{Betreuer}%
}
\newcommand\supervisorsname{%
 \IfLanguageName{english}{Supervisors}{Betreuer}%
}
\newcommand\degreename{Bachelor of Science}
\subject{\kindname}
\newcommand{\supervisor}[1]{%
 \def\@supervisor{#1}
 \publishers{\textbf{\supervisorname:} #1}
}
\newcommand{\supervisors}[1]{%
 \def\@supervisors{#1}
 \publishers{\textbf{\supervisorsname:}
  {
   \def\and{\\}
   \begin{tabular}[t]{l}
   #1
   \end{tabular}
  }
 }
}
\renewcommand\abstract[1]{%
 \global\setbox\absbox=\hbox{#1}%
}
\global\let\@acknowledgments\@empty
\newcommand\acknowledgments[1]{\def\@acknowledgments{#1}}
\newcommand*\frontmatter{%
 \if@twoside\cleardoublepage\else\clearpage\fi
  \@mainmatterfalse\pagenumbering{roman}%
}
\newcommand*\mainmatter{%
 \if@twoside\cleardoublepage\else\clearpage\fi
  \@mainmattertrue\pagenumbering{arabic}%
}
\newcommand*\backmatter{%
\if@openright\cleardoublepage\else\clearpage\fi
  \@mainmatterfalse%
}
\renewcommand*\maketitle[1][-1]{{%
 \setcounter{page}{#1}
 \newgeometry{margin=1in}
 \pagestyle{empty}
 \begin{center}
 {\huge\textbf{\@plaintitle}}
 \vskip3em
 {\Large\textbf{%
  \IfLanguageName{english}{%
   Bachelor Thesis in Computer Science, Security and Privacy Lab
  }{%
   Bachelorarbeit in der Studienrichtung Informatik
  }
 }}
 \vskip3em
 {\Large \IfLanguageName{english}{by}{von}}
 \vskip3em
 {\LARGE\textbf{\@plainauthor}}\par
 \vskip3em
 {\Large\vbox{%
  \IfLanguageName{english}{
   submitted to the University of Innsbruck, \\ Department of Computer Science,
   Security and Privacy Lab \vskip2em
   in partial fulfillment of the requirements \\
   for the degree of \degreename
  }{
   eingereicht an der \\
   Fakult\"at f\"ur Betriebswirtschaft \\
   der Universit\"at Innsbruck
   \vskip2em
   zur Erlangung des akademischen Grades \\
   \degreename
  }
 }}\par
 \vfill
 {\Large
  \vbox{
  \ifx\@supervisors\@empty
  \IfLanguageName{english}{%
   \expandafter\lowercase\expandafter{\supervisorname}%
  }{\supervisorname}%
  : \@supervisor, \mbox{\@institute}
 \else
  \IfLanguageName{english}{%
   \expandafter\lowercase\expandafter{\supervisorsname}%
  }{\supervisorsname}%
  :
  {
   \def\and{, }
    \@supervisors
    \\
   \mbox{\@institute}
  }
 \fi
 }}\par
 \vfill
 {\Large\textbf{Innsbruck, \@date}}
 \end{center}
 \frontmatter
 \thispagestyle{empty}
 \let\footnotesize\small
 \let\footnoterule\relax
 \let\footnote\thanks
 \renewcommand*\thefootnote{\@fnsymbol\c@footnote}%
 \let\@oldmakefnmark\@makefnmark
 \renewcommand*{\@makefnmark}{\rlap\@oldmakefnmark}
 \newbox\cllbox
 \newbox\ifibox
 \newbox\unibox
 \newdimen\logoheight
%\setbox\cllbox=\hbox{\includegraphics[height=30mm]{logos/plmshortlogo.png}}
 \setbox\cllbox=\hbox{\includegraphics[height=40mm]{logos/institute.png}}
%\setbox\ifibox=\hbox{\includegraphics[height=20mm]{logos/institute.png}}
 
 \setbox\unibox=\hbox{\includegraphics[height=30mm]{logos/unilogo.pdf}}
 \logoheight=\ht\cllbox
 \begin{center}
 \hbox to \textwidth{%
  \rlap{\box\cllbox}
  \hfill
  \hbox{\vbox to \logoheight{\vfill\box\ifibox \vfill}}
  \hfill
  \llap{\box\unibox}
 }
 \ifx\@subject\@empty \else
  {\bigskip\Large \@subject \par}
  \vskip 3em
 \fi
 {\titlefont\huge \@title\par}
 \vskip 3em
 {\Large \lineskip 0.75em
 \begin{tabular}[t]{c}
  \@author{}
  \ifx\@matriculationnumber\@empty{}\else(\@matriculationnumber)\fi \\
  \href{mailto:\@mailaddress}{\texttt{\@mailaddress}}
 \end{tabular}\par}
 \vskip 1.5em
 {\Large \@date \par}
 \vskip \z@ \@plus3fill
 {\Large \@publishers \par}
 \vskip 3em
 \end{center}\par
 \@thanks
 \global\let\@thanks\@empty
 \vfill\null
 \vskip 3em
 \@thanks
 %\vfill\null
 \setcounter{footnote}{0}%
 \global\let\thanks\relax
 \global\let\maketitle\relax
 \global\let\@thanks\@empty
 \global\let\@author\@empty
 \global\let\@date\@empty
 \global\let\@title\@empty
 \global\let\@extratitle\@empty
 \global\let\@titlehead\@empty
 \global\let\@subject\@empty
 \global\let\@publishers\@empty
 \global\let\@uppertitleback\@empty
 \global\let\@lowertitleback\@empty
 \global\let\@dedication\@empty
 \global\let\author\relax
 \global\let\title\relax
 \global\let\extratitle\relax
 \global\let\titlehead\relax
 \global\let\subject\relax
 \global\let\publishers\relax
 \global\let\uppertitleback\relax
 \global\let\lowertitleback\relax
 \global\let\dedication\relax
 \global\let\date\relax
 \global\let\and\relax
 \clearpage
\cleardoublepage
}}
\let\@OLDtableofcontents\tableofcontents
\renewcommand\tableofcontents{%
 \pagestyle{empty}
 \cleardoublepage
 \begin{center}
 \normalfont\sectfont\nobreak\abstractname
 \@endparpenalty\@M
 \end{center}
 \unhbox\absbox
 \par\vfil\null
 \ifx\@acknowledgments\@empty{}\else
  \cleardoublepage
  \chapter*{\ackname}
  \@acknowledgments
  \cleardoublepage
 \fi
 \@OLDtableofcontents
\cleardoublepage
 \mainmatter
 \pagestyle{fancy}
 \fancyhead{}
 \fancyfoot{}
 \renewcommand\chaptermark[1]{\markboth{\thechapter\ ##1}{}}
 \renewcommand\sectionmark[1]{\markright{\thesection\ ##1}}
 \renewcommand\headrulewidth{0.5pt}
 \fancyhead[LE]{\leftmark}
 \fancyhead[RO]{\rightmark}
 \fancyfoot[LE,RO]{\thepage}
}
\endinput
%%
%% End of file `plmmthesis.cls'.

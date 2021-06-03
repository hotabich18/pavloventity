function ChangeOver(x) {
 var wordClass = x.className;
 var parent = x.parentNode;
 if (parent.className == 'sentence')
 {
 parent.style = "background-color:khaki";
 x.style = "background-color:none";
 }
 else
 {
 x.style = "background-color:khaki";
 }
 if (wordClass == 'word' && x.innerHTML != ',' && x.innerHTML != '.' && x.innerHTML != '?' && x.innerHTML != '!' && x.innerHTML != '...')
 {
 x.style = "background-color:green";
 }

<!-- console.log(x);-->
<!-- console.log(parent);-->
};

function ChangeOut(x) {
 x.style = "background-color:none";
}

function RightClick(x) {
 sessionStorage['wordid'] = x.id;
 sessionStorage['sentenceid'] = x.parentNode.id;
 sessionStorage['paragraphid'] = x.parentNode.parentNode.id;
<!--    alert(sessionStorage['paragraphid'] + ' ' + sessionStorage['sentenceid'] + ' ' + sessionStorage['wordid']);-->
<!--console.log(x.parentNode.parentNode)-->
}

/**
 * @param {HTMLElement} element Элемент, имя тэга которого будет заменено.
 * @param {String} newTagName Новое имя тэга.
 */
function replaceTag(element, newTagName) {
    // Создаём новый тэг.
    var newTag = document.createElement(newTagName);

    // Вставляем новый тэг перед старым.
    element.parentElement.insertBefore(newTag, element);

    // Переносим в новый тэг атрибуты старого с их значениями.
    for (var i = 0, attrs = element.attributes, count = attrs.length; i < count; ++i)
        newTag.setAttribute(attrs[i].name, attrs[i].value);

    // Переносим в новый тэг все дочерние элементы старого.
    var childNodes = element.childNodes;
    while (childNodes.length > 0)
        newTag.appendChild(childNodes[0]);

    // Удаляем старый тэг.
    element.parentElement.removeChild(element);
}

const attachContextMenu = (() => {
  const contextMenu = document.createElement('ul');

  const hideOnResize = () => hideMenu(true);

  function hideMenu(e) {
    if (e === true || !contextMenu.contains(e.target)) {
      contextMenu.remove();
      document.removeEventListener('click', hideMenu);
      window.removeEventListener('resize', hideOnResize);
    }
  };

  const attachOption = (target, opt) => {
    const item = document.createElement('li');
    item.className = 'context-menu-item';
    item.innerHTML = `<span>${opt.label}</span>`;
    item.addEventListener('click', e => {
      e.stopPropagation();
      if (!opt.subMenu || opt.subMenu.length === 0) {
        opt.action(opt);
        hideMenu(true);
      }
    });

    target.appendChild(item);

    if (opt.subMenu && opt.subMenu.length) {
      const subMenu = document.createElement('ul');
      subMenu.className = 'context-sub-menu';
      item.appendChild(subMenu);
      opt.subMenu.forEach(subOpt => attachOption(subMenu, subOpt));
    }
  };

  const showMenu = (e, menuOptions) => {
    e.preventDefault();
    contextMenu.className = 'context-menu';
    contextMenu.innerHTML = '';
    menuOptions.forEach(opt => attachOption(contextMenu, opt));
    document.body.appendChild(contextMenu);

    const { innerWidth, innerHeight } = window;
    const { offsetWidth, offsetHeight } = contextMenu;
    let x = 0;
    let y = 0;

    if (e.clientX >= innerWidth / 2) {
      contextMenu.classList.add('left');
    }

    if (e.clientY >= innerHeight / 2) {
      contextMenu.classList.add('top');
    }

    if (e.clientX >= innerWidth - offsetWidth) {
      x = '-100%';
    }

    if (e.clientY >= innerHeight - offsetHeight) {
      y = '-100%';
    }

    contextMenu.style.left = e.clientX + 'px';
    contextMenu.style.top = e.clientY + 'px';
    contextMenu.style.transform = `translate(${x}, ${y})`;
    document.addEventListener('click', hideMenu);
    window.addEventListener('resize', hideOnResize);
  };

  return (el, options) => {
    el.addEventListener('contextmenu', e => showMenu(e, options));
  };
})();

document.querySelectorAll('span').
forEach(btn => {
  attachContextMenu(btn, [
  { label: "Изменить тип слова", action(o) {console.log(o);},
    subMenu: [
    {% for type in types %}
        { label: '{{type['name']}}', action(e) {

<!--         console.log(e.target);-->
            var paragraphid = sessionStorage['paragraphid'];
            var sentenceid = sessionStorage['sentenceid'];
            var wordid = sessionStorage['wordid'];
            var word = document.querySelector("[id='"+sessionStorage['paragraphid']+"'] [id='"+ sessionStorage['sentenceid']+"'] [id='"+sessionStorage['wordid']+"']");
            word.style.backgroundColor = '{{type['color']}}';
            word.title = '{{type['description']}}';
            word.classList.add("card");
            word.removeAttribute("onmouseover");
            word.removeAttribute("onmouseout");
            replaceTag(word, 'a');
<!--    alert(sessionStorage['paragraphid'].id + ' ' + sessionStorage['sentenceid'].id + ' ' + sessionStorage['wordid'].id);-->
<!--         console.log(e.target.parent);-->

<!--        console.log('{{type['description']}}');-->


        } },
    {% endfor %}] },

  { label: "Удалить сущность", action(o) {

    var word = document.querySelector("[id='"+sessionStorage['paragraphid']+"'] [id='"+ sessionStorage['sentenceid']+"'] [id='"+sessionStorage['wordid']+"']");
    console.log(word);
    word.removeAttribute("style");
    word.removeAttribute("title");
    word.classList.remove("card");
    word.setAttribute("onmouseout", "ChangeOut(this)");
    word.setAttribute("onmouseover", "ChangeOver(this)");
    replaceTag(word, 'span');
  } },
    { label: "Отправить предложение на переобучение", action(o) {

  console.log(o);

  },


  }]);
});
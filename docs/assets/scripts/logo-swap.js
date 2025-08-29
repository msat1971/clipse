document.addEventListener('DOMContentLoaded', () => {
  const logoImg = document.querySelector('.md-header__button.md-logo img');
  if (!logoImg) return;

  const LIGHT = 'assets/images/Logo_Brand_Dawg_Light.svg';
  const DARK = 'assets/images/Logo_Brand_Dawg_Dark.svg';

  const resolve = (path) => new URL(path, document.baseURI).href;

  const updateLogo = () => {
    const isDark = document.documentElement.getAttribute('data-md-color-scheme') === 'slate';
    const target = resolve(isDark ? DARK : LIGHT);
    if (!logoImg.getAttribute('alt')) logoImg.setAttribute('alt', 'Brand Dawg Logo');
    if (logoImg.src !== target) logoImg.src = target;
  };

  updateLogo();
  const observer = new MutationObserver(updateLogo);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-md-color-scheme'] });
});

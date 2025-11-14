// Esta função encapsula a lógica da animação 3D para ser reutilizada
export function useCardTiltAnimation() {
  const handleCardMouseMove = (evt: MouseEvent) => {
    const card = evt.currentTarget as HTMLElement;
    const { top, left, width, height } = card.getBoundingClientRect();
    const x = evt.clientX - left;
    const y = evt.clientY - top;

    // Calcula a rotação baseada na posição do mouse dentro do card
    const rotateX = -12 * ((y - height / 2) / height);
    const rotateY = 12 * ((x - width / 2) / width);

    // Aplica o efeito 3D
    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
  };

  const resetCardTransform = (evt: MouseEvent) => {
    const card = evt.currentTarget as HTMLElement;
    card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
  };

  return { handleCardMouseMove, resetCardTransform };
}
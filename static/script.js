const left = document.querySelector('.left')
const leftmid = document.querySelector('.leftmid')
const rightmid = document.querySelector('.rightmid')
const right = document.querySelector('.right')
const container = document.querySelector('.container')

left.addEventListener('mouseenter', ()=> container.classList.add('hover-left'))
left.addEventListener('mouseleave', ()=> container.classList.remove('hover-left'))

leftmid.addEventListener('mouseenter', ()=> container.classList.add('hover-leftmid'))
leftmid.addEventListener('mouseleave', ()=> container.classList.remove('hover-leftmid'))

rightmid.addEventListener('mouseenter', ()=> container.classList.add('hover-rightmid'))
rightmid.addEventListener('mouseleave', ()=> container.classList.remove('hover-rightmid'))

right.addEventListener('mouseenter', ()=> container.classList.add('hover-right'))
right.addEventListener('mouseleave', ()=> container.classList.remove('hover-right'))
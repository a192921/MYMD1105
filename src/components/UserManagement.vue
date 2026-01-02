<template>
  <a-table
    bordered
    :columns="columns"
    :data-source="data"
    :scroll="{ x: 'max-content' }"
  />
</template>

<script setup>
import { reactive } from 'vue'

const data = [
  { key: 1, name: 'Queena', age: 25, job: 'Engineer' },
  { key: 2, name: 'Amy', age: 30, job: 'Designer' },
]

/* ✅ 你指定的 function */
const resizeColumn = (width, column) => {
  column.width = Math.max(width, 80)
}

let startX = 0
let startWidth = 0
let activeColumn = null

const onMouseMove = (e) => {
  if (!activeColumn) return
  resizeColumn(startWidth + e.clientX - startX, activeColumn)
}

const onMouseUp = () => {
  activeColumn = null
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
}

const columns = reactive([
  {
    title: 'Name',
    dataIndex: 'name',
    width: 150,
    customHeaderCell: (column) => ({
      style: {
        width: column.width + 'px',
        position: 'relative',
      },
      onMousedown: (e) => {
        // 只在右側拖曳線才啟動
        if (!e.target.classList.contains('resize-handle')) return
        e.preventDefault()

        startX = e.clientX
        startWidth = column.width
        activeColumn = column

        document.addEventListener('mousemove', onMouseMove)
        document.addEventListener('mouseup', onMouseUp)
      },
    }),
  },
  {
    title: 'Age',
    dataIndex: 'age',
    width: 100,
    customHeaderCell: (column) => ({
      style: {
        width: column.width + 'px',
        position: 'relative',
      },
      onMousedown: (e) => {
        if (!e.target.classList.contains('resize-handle')) return
        e.preventDefault()

        startX = e.clientX
        startWidth = column.width
        activeColumn = column

        document.addEventListener('mousemove', onMouseMove)
        document.addEventListener('mouseup', onMouseUp)
      },
    }),
  },
  {
    title: 'Job',
    dataIndex: 'job',
    width: 200,
    customHeaderCell: (column) => ({
      style: {
        width: column.width + 'px',
        position: 'relative',
      },
      onMousedown: (e) => {
        if (!e.target.classList.contains('resize-handle')) return
        e.preventDefault()

        startX = e.clientX
        startWidth = column.width
        activeColumn = column

        document.addEventListener('mousemove', onMouseMove)
        document.addEventListener('mouseup', onMouseUp)
      },
    }),
  },
])
</script>

<style>
/* 🔑 拖曳線一定要真的存在 */
.ant-table-thead th {
  position: relative;
}

.resize-handle {
  position: absolute;
  right: 0;
  top: 0;
  width: 6px;
  height: 100%;
  cursor: col-resize;
  z-index: 10;
}

/* 用 pseudo-element 產生拖曳線 */
.ant-table-thead th::after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  width: 6px;
  height: 100%;
  cursor: col-resize;
}
</style>

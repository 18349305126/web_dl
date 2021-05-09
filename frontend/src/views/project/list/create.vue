<template>
  <project-detail :is-edit="false" />
</template>

<script>
import ProjectDetail from './components/ProjectDetail'

export default {
  name: 'CreateProject',
  components: { ProjectDetail }
}
</script>

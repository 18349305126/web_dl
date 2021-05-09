<template>
  <dataset-detail :is-edit="true" />
</template>

<script>
import DatasetDetail from './components/DatasetDetail'

export default {
  name: 'EditDataset',
  components: { DatasetDetail }
}
</script>

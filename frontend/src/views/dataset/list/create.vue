<template>
  <dataset-detail :is-edit="false" />
</template>

<script>
import DatasetDetail from './components/DatasetDetail'

export default {
  name: 'CreateDataset',
  components: { DatasetDetail }
}
</script>

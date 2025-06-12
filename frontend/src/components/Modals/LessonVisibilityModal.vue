<template>
    <Dialog
      v-model="show"
      :options="{
        title: __('Manage Lesson Visibility'),
        size: 'lg',
        actions: [
          {
            label: __('Close'),
            variant: 'solid',
            onClick: (close) => close(),
          },
        ],
      }"
    >
      <template #body-content>
        <div v-if="courses.data?.length" class="space-y-6">
          <div v-for="course in courses.data" :key="course.name" class="border rounded-lg p-4">
            <div class="text-lg font-semibold mb-4">{{ course.title }}</div>
            <div v-if="courseLessons[course.name]?.length" class="space-y-2">
              <div v-for="lesson in courseLessons[course.name]" :key="lesson.name" class="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                <div class="flex items-center space-x-2">
                  <span class="text-sm">{{ lesson.title }}</span>
                </div>
                <FormControl
                  v-model="lesson.hidden_from_students"
                  type="checkbox"
                  :label="__('Hidden from Students')"
                  @change="handleVisibilityChange(lesson)"
                />
              </div>
            </div>
            <div v-else class="text-sm text-gray-500 italic">
              {{ __('No lessons in this course') }}
            </div>
          </div>
        </div>
        <div v-else class="text-sm text-gray-500 italic">
          {{ __('No courses in this batch') }}
        </div>
      </template>
    </Dialog>
  </template>
  
  <script setup>
  import { ref, inject } from 'vue'
  import { Dialog, FormControl, createResource, toast } from 'frappe-ui'
  
  const show = defineModel()
  const user = inject('$user')
  
  const props = defineProps({
    batch: {
      type: String,
      required: true,
    },
  })
  
  const courses = createResource({
    url: 'lms.lms.utils.get_batch_courses',
    params: {
      batch: props.batch,
    },
    cache: ['batchCourses', props.batch],
    auto: true,
    onSuccess(data) {
      console.log('Batch courses data:', data)
      // Fetch lessons for each course
      data.forEach(course => {
        getCourseLessons(course.name)
      })
    }
  })
  
  const courseLessons = ref({})
  
  const getCourseLessons = (courseName) => {
    console.log('Fetching lessons for course:', courseName)
    const lessonsResource = createResource({
      url: 'lms.lms.utils.get_course_lessons',
      params: {
        course: courseName,
        batch: props.batch
      },
      auto: true,
      onSuccess(data) {
        console.log('Lessons data for course', courseName, ':', data)
        courseLessons.value[courseName] = data
      }
    })
  }
  
  const updateVisibilityResource = createResource({
    url: 'lms.lms.api.update_lesson_visibility',
    makeParams(values) {
      return {
        batch: props.batch,
        lesson: values.name,
        hidden: values.hidden_from_students,
      }
    },
  })
  
  const handleVisibilityChange = (lesson) => {
    updateVisibilityResource.submit(
      {
        lesson: lesson.name,
        hidden: lesson.hidden_from_students,
      },
      {
        onSuccess() {
          toast.success(__('Lesson visibility updated'))
        },
        onError(err) {
          toast.error(err.messages?.[0] || err)
        },
      }
    )
  }
  </script>
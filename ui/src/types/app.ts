export interface AppStep {
  id: number
  version: string
  name: string
  Description: string
  input: Array<{
    name: string
    type: string
    description: string
    required: boolean
  }>
  output?: Array<{
    name: string
    type: string
    description: string
    required?: boolean
  }>
  depends_on: number[]
}

export interface SubApp {
  id: number
  name: string
  Description: string
  version: string
  steps: AppStep[]
}

export interface App {
  id: number
  name: string
  Description: string
  version: string
  sub_apps?: SubApp[]
  steps?: AppStep[]
}
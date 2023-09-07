/*******************************************************************************
 * Copyright 2013-2021 Aerospike, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 ******************************************************************************/

#pragma once

// pyval is a PyObject* classname is a string
#define AS_Matches_Classname(pyval, classname)                                 \
    (strcmp((pyval)->ob_type->tp_name, (classname)) == 0)

static inline void PyObject_SetAttrStringSafe(PyObject *obj,
                                              const char *attr_name,
                                              PyObject *value)
{
    if (value == NULL) {
        PyObject_DelAttrString(obj, attr_name);
    }
    else {
        PyObject_SetAttrString(obj, attr_name, value);
    }
}

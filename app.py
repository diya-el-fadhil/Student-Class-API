from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

students = {}
classes = {}
student_class_registrations = {}

def validate_student_data(data, required_fields=None):
    if required_fields is None:
        required_fields = ['FirstName', 'LastName', 'Age', 'City']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing or empty field: {field}"
    
    try:
        age = int(data['Age'])
        if age <= 0 or age > 150:
            return False, "Age must be a positive number between 1 and 150"
    except (ValueError, TypeError):
        return False, "Age must be a valid number"
    
    return True, "Valid"

def validate_class_data(data, required_fields=None):
    if required_fields is None:
        required_fields = ['ClassName', 'Description', 'StartDate', 'EndDate', 'NumberOfHours']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing or empty field: {field}"
    
    try:
        start_date = datetime.strptime(data['StartDate'], '%Y-%m-%d')
        end_date = datetime.strptime(data['EndDate'], '%Y-%m-%d')
        if end_date <= start_date:
            return False, "End date must be after start date"
    except ValueError:
        return False, "Dates must be in YYYY-MM-DD format"
    
    try:
        hours = int(data['NumberOfHours'])
        if hours <= 0:
            return False, "Number of hours must be positive"
    except (ValueError, TypeError):
        return False, "Number of hours must be a valid number"
    
    return True, "Valid"

@app.route('/students', methods=['POST'])
def create_student():
    try:
        data = request.get_json()
        
        is_valid, message = validate_student_data(data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        student_id = str(uuid.uuid4())
        
        student = {
            'StudentId': student_id,
            'FirstName': data['FirstName'],
            'LastName': data['LastName'],
            'MiddleName': data.get('MiddleName', ''),  # Optional field
            'Age': int(data['Age']),
            'City': data['City'],
            'CreatedAt': datetime.now().isoformat()
        }
        
        students[student_id] = student
        
        return jsonify({
            'message': 'Student created successfully',
            'student': student
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        if student_id not in students:
            return jsonify({'error': 'Student not found'}), 404
        
        data = request.get_json()
        
        provided_fields = [field for field in ['FirstName', 'LastName', 'Age', 'City'] if field in data]
        if provided_fields:
            is_valid, message = validate_student_data(data, provided_fields)
            if not is_valid:
                return jsonify({'error': message}), 400
        
        student = students[student_id]
        if 'FirstName' in data:
            student['FirstName'] = data['FirstName']
        if 'LastName' in data:
            student['LastName'] = data['LastName']
        if 'MiddleName' in data:
            student['MiddleName'] = data['MiddleName']
        if 'Age' in data:
            student['Age'] = int(data['Age'])
        if 'City' in data:
            student['City'] = data['City']
        
        student['UpdatedAt'] = datetime.now().isoformat()
        
        return jsonify({
            'message': 'Student updated successfully',
            'student': student
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        if student_id not in students:
            return jsonify({'error': 'Student not found'}), 404
        
        registrations_to_remove = []
        for reg_id, registration in student_class_registrations.items():
            if registration['StudentId'] == student_id:
                registrations_to_remove.append(reg_id)
        
        for reg_id in registrations_to_remove:
            del student_class_registrations[reg_id]
        
        deleted_student = students[student_id]
        del students[student_id]
        
        return jsonify({
            'message': 'Student deleted successfully',
            'deleted_student': deleted_student
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/students', methods=['GET'])
def get_all_students():
    return jsonify({
        'students': list(students.values()),
        'total_count': len(students)
    }), 200

@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify({'student': students[student_id]}), 200

@app.route('/classes', methods=['POST'])
def create_class():
    try:
        data = request.get_json()
        
        is_valid, message = validate_class_data(data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        class_id = str(uuid.uuid4())
        
        class_info = {
            'ClassId': class_id,
            'ClassName': data['ClassName'],
            'Description': data['Description'],
            'StartDate': data['StartDate'],
            'EndDate': data['EndDate'],
            'NumberOfHours': int(data['NumberOfHours']),
            'CreatedAt': datetime.now().isoformat()
        }
        
        classes[class_id] = class_info
        
        return jsonify({
            'message': 'Class created successfully',
            'class': class_info
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/classes/<class_id>', methods=['PUT'])
def update_class(class_id):
    try:
        if class_id not in classes:
            return jsonify({'error': 'Class not found'}), 404
        
        data = request.get_json()
        
        provided_fields = [field for field in ['ClassName', 'Description', 'StartDate', 'EndDate', 'NumberOfHours'] if field in data]
        if provided_fields:
            is_valid, message = validate_class_data(data, provided_fields)
            if not is_valid:
                return jsonify({'error': message}), 400
        
        class_info = classes[class_id]
        if 'ClassName' in data:
            class_info['ClassName'] = data['ClassName']
        if 'Description' in data:
            class_info['Description'] = data['Description']
        if 'StartDate' in data:
            class_info['StartDate'] = data['StartDate']
        if 'EndDate' in data:
            class_info['EndDate'] = data['EndDate']
        if 'NumberOfHours' in data:
            class_info['NumberOfHours'] = int(data['NumberOfHours'])
        
        class_info['UpdatedAt'] = datetime.now().isoformat()
        
        return jsonify({
            'message': 'Class updated successfully',
            'class': class_info
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/classes/<class_id>', methods=['DELETE'])
def delete_class(class_id):
    try:
        if class_id not in classes:
            return jsonify({'error': 'Class not found'}), 404
        
        registrations_to_remove = []
        for reg_id, registration in student_class_registrations.items():
            if registration['ClassId'] == class_id:
                registrations_to_remove.append(reg_id)
        
        for reg_id in registrations_to_remove:
            del student_class_registrations[reg_id]
        
        deleted_class = classes[class_id]
        del classes[class_id]
        
        return jsonify({
            'message': 'Class deleted successfully',
            'deleted_class': deleted_class
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/classes', methods=['GET'])
def get_all_classes():
    return jsonify({
        'classes': list(classes.values()),
        'total_count': len(classes)
    }), 200

@app.route('/classes/<class_id>', methods=['GET'])
def get_class(class_id):
    if class_id not in classes:
        return jsonify({'error': 'Class not found'}), 404
    
    return jsonify({'class': classes[class_id]}), 200

@app.route('/registrations', methods=['POST'])
def register_student_to_class():
    try:
        data = request.get_json()
        
        if 'StudentId' not in data or 'ClassId' not in data:
            return jsonify({'error': 'StudentId and ClassId are required'}), 400
        
        student_id = data['StudentId']
        class_id = data['ClassId']
        
        if student_id not in students:
            return jsonify({'error': 'Student not found'}), 404
        
        if class_id not in classes:
            return jsonify({'error': 'Class not found'}), 404
        
        for registration in student_class_registrations.values():
            if registration['StudentId'] == student_id and registration['ClassId'] == class_id:
                return jsonify({'error': 'Student is already registered for this class'}), 400
        
        registration_id = str(uuid.uuid4())
        registration = {
            'RegistrationId': registration_id,
            'StudentId': student_id,
            'ClassId': class_id,
            'RegistrationDate': datetime.now().isoformat(),
            'StudentName': f"{students[student_id]['FirstName']} {students[student_id]['LastName']}",
            'ClassName': classes[class_id]['ClassName']
        }
        
        student_class_registrations[registration_id] = registration
        
        return jsonify({
            'message': 'Student registered to class successfully',
            'registration': registration
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/classes/<class_id>/students', methods=['GET'])
def get_students_in_class(class_id):
    try:
        if class_id not in classes:
            return jsonify({'error': 'Class not found'}), 404
        
        registered_students = []
        for registration in student_class_registrations.values():
            if registration['ClassId'] == class_id:
                student_id = registration['StudentId']
                if student_id in students:  # Make sure student still exists
                    student_info = students[student_id].copy()
                    student_info['RegistrationDate'] = registration['RegistrationDate']
                    student_info['RegistrationId'] = registration['RegistrationId']
                    registered_students.append(student_info)
        
        class_info = classes[class_id]
        
        return jsonify({
            'class': class_info,
            'registered_students': registered_students,
            'total_students': len(registered_students)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/registrations', methods=['GET'])
def get_all_registrations():
    return jsonify({
        'registrations': list(student_class_registrations.values()),
        'total_count': len(student_class_registrations)
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Student Management API is running',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

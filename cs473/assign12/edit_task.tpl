%#template for editing a task
%#the template expects to receive a value for "no" as well a "old", the text of the selected ToDo item

<a href="/">Task List</a></br>
<p>Edit the task with ID = {{no}}</p>

<form action="/edit/{{no}}" method="post">
<input type="text" name="task" value="{{txt}}" size="100" maxlength="100">
<select name="status">
%if stat == "1":
<option selected="selected">open</option>
<option>closed</option>
%else:
<option>open</option>
<option selected="selected">closed</option>
%end
</select>
<br/>
<input type="submit" name="save" value="save">
</form>

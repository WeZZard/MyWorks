---
title: "Swift Macro: Revisited - The Concept"
category: Programming
tags: [Swift, Macro]
---

---

- Further directions:
  - More IDE collaboration: syntax highlighting

---

From relative sessions of WWDC 2023, we've learned that Swift macro aims
to:

- Eliminate boilerplates
- Make tedious things easy
- Share with other developers in packages

However, these goals are not exclusive to Swift macro; they are common
targets for most common language features in Swift such as function, type
and module. One could argue that all high-level programming languages
aspire to these ends. There must be something else that Swift Macro excels
at, otherwise, it would be redundant.

So, what is it that Swift Macro does exceptionally well?

The answer to this question is critical. It would inspire us to create
Swift macros that hit the points, tell us the boundaries of behaviors
while creating Swift macros, and ultimately guide us to ship
better-designed Swift macros. This is the essence of Swift macro.

To have this answer, we must first comprehend the problems that existing
Swift language features like function, type and module have managed to
solve and their limitations. The key to understanding Swift macro lies in
this exploration.

## An Exploration of Existing Reuse Features

TODO: Function & structured programming could be merged

"Function" is a common concept in almost all programming languages. Though
it may have different names in different languages like subroutine,
routine, subprogram or procedure, those names are sharing the same idea
which is to offer reusable execution units for the programmers. This has
not been changed since the concept of function was initially conceived
during the work of ENIAC — the world's first computer, and introduced in
FORTRAN with the name "subroutine".

TODO: An example of the FORTRAN subroutine.

But people then have found that programs would be better understood if:

- Variables are only accessible within the block of a control structure
  like the `IF` statement or loop.
- Control structures could be more expressive like using
  `IF-THEN-ELSE-END` instead of a simple `IF` statement.
- The `GOTO` statement could be eliminated by more advanced control
  structures.
- The "function" could be defined within other "functions".

All these points above comprised the concept of structured programming,
which was coined by Edwards W. Dijkstra. In the meanwhile, he also imbued
these ideas into the ALGO 60 programming language.

TODO: An example of ALGO 60's structured programming

The joining of structured programming broadened the number of programmers
since the programs were easier to understand than before. When people were
trying to use computer programs to solve more and more real-world
problems, difficulties in code management ensued because there were only
functions available for organizing the code -- this means that people can
only reuse the code at the smallest granular level.

A programming language called Simula, which encoded designing for
simulating real-world processes in its name, enriched the granularity in
code reuse by introducing a concept called object-oriented programming.
With this concept, developers can create types that have a bunch of
variables and functions declared as members of a type that are accessed
via dot notations. The members of a type is scoped within the type. You
can only access them with the instance name. On top of that, a type can
reuse a type by inheriting it.

TODO: Figure: dot notation and type inheritance

However, there are still challenges lied before programmers. How to reuse
code between projects? Copy and paste? How to accelerate compilation by
avoiding the commonly reused code? Buy more powerful machines? Modula, a
programming language as a decedent of Pascal, answered these questions by
introducing a concept called module, which keeps developers away from
tedious pushes on keyboards and money talks.

Modules brought by Modula enabled encapsulation of code on a granular
level greater than types. More than that, this feature also brought
separate compilation and segregation between interfaces and
implementations which bring faster build speed and better software design.
These advantages now emerge in Swift modules.

TODO: Figure: module-level code reuse and lexical scope

## What Swift Macros Do Exceptionally Well?

By exploring the development history of code reusing, we can find that
people tend to create concepts that aggregate the smaller ones and
"umbrella" them with a protection mechanism. Let me give you examples:

- Functions aggregate execution flows and variables and "umbrella" them
  with control structures and lexical scopes;
- Types aggregate variables and functions and "umbrella" them with
  instance name or type name;
- Modules aggregate variables, types and functions and "umbrellas" them
  with the module's namespaces;

These help us keep the program easy to understand as the code size
increases.

But we can find there are still many critical programming concepts that
cannot be encapsulated with them. Let me show you some examples.

### Compile-Time Checked Literals

Since design software like Figma or Sketch represents the RGB color with 6
hexadecimal digits, the developers would often have the following
extension in Swift such that they can directly copy and paste the RGB
value displayed in the design software to the code:

```swift
import SwiftUI

// Color extension
extension Color {

  public init(_ hex: UInt)

}

// Use example
Color(0xFFEEAA)
```

But how do I know this is a valid RGB color? Since we are copying and
pasting, the digits themselves could be shorter than what it was in the
original place.

```swift
// Invalid color.
Color(0xFFEEA)
```

With Swift macro, these "literals" could be checked at compile-time:

TODO: Replace it with a diagram

```swift
#Color(0xFFEEAA) // compiled
#Color(0xFFEEA) // invalid, not compiled
```

### Code Style

In real-world programming, we always want to get rid of the following
code:

```swift
func foo(_ bar: Int?) {
  print(bar!)
}
```

Instead, we prefer the code like below:

```swift
func foo(_ bar: Int?) {
  guard let bar else {
    return
  }
  print(bar)
}
```

But it's tedious. You may have to `guard let ... else` many times in one
single function's body if you are overriding methods naïvely bridged from
Objective-C, or a large-scale legacy code base finally chose to make
parameters nullable by default because of the impossible workload of
nullability verification. This heavy form of safety guarantee waters
things down. We don't have to write a lot of code to do a trivial thing.

However, since a function protects its internal execution flow for the
sake of structured programming, we cannot encapsulate this
`guard let ... else` in a function -- because the `return` statement in a
function cannot make the caller site function to exit.

```swift
func guard<T>(_ value: T?) -> T {
  guard let value else {
    // This return cannot help `foo` to exit.
    // More than that, this function does not compile.
    return
  }
  return value
}

func foo(_ bar: Int?) {
  let bar = guard(bar)
  print(bar)
}
```

But Swift Macro does not have this constraint. We can have a macro called
`#unwrapped` which is used as the code shown below:

```swift
func foo(_ bar: Int?) {
  #unwrapeped(bar) {
    print(bar)
  }
}
```

And expanded as:

```swift
func foo(_ bar: Int?) {
  // #unwrapped expansion began
  guard let bar = bar else {
    return
  }
  print(bar)
  // #unwrapped expansion ended
}
```

Then the control flow of the `foo` function could be affected by the
`#unwrapped` macro now. More than that, the variable `bar` received by the
`print` function is the variable declared by the `guard let bar` statement
which is also brought by the expansion of `#unwrapped` macro. This shows
that the expansions of Swift macros share the lexical scope of the applied
site.

From what we've learned, we can have a conclusion that with Swift macro we
can encapsulate programming concepts that **involve control flow
manipulations** and **lexical scope sharing**.

### Extending Type's Behavior

The capabilities of Swift Macro are not limited to these. Let's consider
another example to showcase the expansive potential of Swift Macro.

In real-world programming stories, we always start from simple structs
like the below:

```swift
struct User {

  var name: String

  var avatar: URL

}
```

But as the size of the repository grows, the struct may grow at the same
speed:

```swift
struct User {

  var name: String

  var avatar: URL

  var avatarsInDifferentScales: [Int : URL]

  var userID: String

  var socialMedias: [String]

  var brief: String

  // ...

}
```

Since each property in the `struct` I showed above engaged a heap storage
allocation to store the data, the cost of copying this struct is increased
at the same time -- the count of heap storage here means the count of
object retain operations and retaining shall be guaranteed to be atomic.
This may cause lagging in user interactions and waste in memory space. By
adopting this technique to several heavily used `struct`s of a real app
produced by ByteDance, I've improved the user interaction by increasing
the fps from 48fps to 56fps and decreasing 600MB memory usage.

TODO: Before-after comparison for the optimization of the app I mentioned

To reduce the cost of copying the struct, we can aggregate the properties
to a class instance which is supposed to be the storage, then implement
the copy-on-write behavior on the original struct when we are mutating the
contents in the storage:

```swift
struct User {

  private class Storage {

    var name: String

    // other properties ...

  }

  private var _storage: Storage

  init(name: String, ...) {
    self._storage = Storage(name: name, ...)
  }

  private func makeStorageUniqueIfNeeded() {
    if !isKnownUniquelyReferenced(&_storage) {
      _storage = Storage(name: name, ...)
    }
  }

  var name: String {
    get { return _storage.name }
    set {
      makeStorageUniqueIfNeeded()
      _storage.name = newValue
    }
  }

}
```

But, again, this is tedious. We not only have to write a lot of code to
reduce the cost of copying that struct but, worse still, it increased the
cost of maintaining the program. With Swift Macro, we can do this more
elegantly.

```swift
@COW
struct User {

  var name: String

  var avatar: URL

  var avatarsInDifferentScales: [Int : URL]

  var userID: String

  var socialMedias: [String]

  var brief: String

  // ...

}
```

Yes. Just as simple as I've shown. By adding an `@COW` attribute to the
struct, we have introduced the copy-on-write behavior to this struct. What
this macro did is nothing more than what we have hand-wired in the
previous code. However, the cost of maintaining the program has not
increased this time.

```swift
struct User {

  // @COW expansion began
  private class Storage {

    var name: String

    // other properties ...

  }

  private var _$storage: Storage

  private func makeStorageUniqueIfNeeded() {
    if !isKnownUniquelyReferenced(&_$storage) {
      _$storage = Storage(name: name, ...)
    }
  }

  init(name: String, ...) {
    self._storage = Storage(name: name, ...)
  }
  // @COW expansion ended

  // @COW expansion began
  @COWIncluded(storage: _$storage)
  // @COW expansion ended
  var name: String {
    // @COWIncluded expansion began
    get { return _$storage.name }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.name = newValue
    }
    // @COWIncluded expansion ended
  }

}
```

TODO: Introduce a more sophisticated encapsulation that I've done

Till now, we can observe that:

- Swift Macro is a way of encapsulation. What you are unable to do before
  Swift Macro got introduced remains the same.
- Swift Macro generates codes by understanding the programmer's code at
  the compile time. This means that we can also do compile-time checking
  with the programmer's code.
- Freestanding Swift macros in a function can affect the control flow of a
  function and implicitly share the lexical scope of the applied site.
- Attached Swift macros can extend members to types or accessors to
  properties. The extended contents also share the same "namespace" of the
  extended point.

These properties not only offer the programmers yet another option for
code reuse but also enable them to encapsulate programming concepts that
may involve compile-time checking, control flow manipulations and adding
behaviors to types without inheritance or other runtime techniques. This
has never been implemented in Swift before. Yet, they are the essence of
Swift Macro.

## Pitfalls of Swift Macros

The examples of Swift macro work "so far so good" till now. However, can
we be confident and bold, implementing any Swift macro we want now?

No.

What brings Swift Macro advantages also brings pitfalls. There are at
least several pitfalls that I've found could lead to dead ends.

### Control Flow in Chaos

TODO: TBD

### Name Conflicts

In the previous example of `#unwrap`, the `bar` variable is re-bound by
the `#unwarp` macro after the macro was expanded.

```swift
func foo(_ bar: Int?) {
  // #unwrapped expansion began
  guard let bar = bar else {
    return
  }
  print(bar)
  // #unwrapped expansion ended
}
```

This brought variable name shadowing where the `guard let bar: Int`
shadows the argument `_ bar: Int?`. In the case of `#unwrap`, the variable
name shadowing is trivial because it is an expected behavior. But
shadowing variables other than the `Optional`s could be considered as
unrecommended practice in real-world programming -- in fact, that would
not be compiled in Swift. As I concluded before, freestanding Swift macro
implicitly shares the lexical scope of the applied site. This enables
potential variable shadowing in macro applications. Here is an example,
the variable name `updater` is shadowed due to the macro expansion:

```swift
func foo(_ bar: Int?) {
  let updater = Updater()
  #unwrap(fee, foe, fum) {
    let updater = Updater()
    print(bar)
    updater.update()
  }
  print(updater.description)
}
```

This could be expanded as the following code:

```swift
func foo(_ bar: Int?) {
  // `updater` defined the first time
  let updater = Updater()
  // #unwrap expansion began
  guard let bar else {
    return
  }
  // `updater` defined the second time
  let updater = Updater()
  print(bar)
  updater.update()
  // #unwrap expansion ended
  print(updater.description)
}
```

By executing the build command in Xcode, you could find this expansion
could not be compiled:

TODO: A figure shows the compilation failure for the code above

The compiler reported that the second declaration of `updater` is an
invalid redeclaration.

More than that, this potential name conflict not only be possible when
freestanding macros meet functions but also be possible when attached
macros meet type declarations.

You may have noticed that there is a member added in the expansion of the
`@COW` macro that uses a name pattern that prefixes with `_$`.

```swift
  private var _$storage: Storage
```

This is a naming convention I learned from Apple's implementation of the
macros in Swift Observation and SwiftData which keeps the implementation
details of an attached macro from the programmer's unintentional access.

But this does not protect those members from unintentional redeclaration
or access brought by other macros -- there could be another macro applied
by the programmer that also adds members with the same name or uses the
member added by other macros. Let's say there was a macro called
`@DictionaryLike` which makes the applied type behaves like a dictionary
by adding a pair of `subscript` getter and setter. Imagine
`@DictionaryLike` was applied on the `User` struct I've shown above:

```swift
@DictionaryLike
struct User {

  // Other contents ...

}
```

The `@DictionaryLike` could be expanded as the following code:

```swift
@DictionaryLike
struct User {

  // Other contents ...

  // @DictionaryLike exapnsion began
  var _$storage: [String : Any] = [:]

  subscript(_ key: String) -> Any? {
    get { return _$storage[key] }
    set { _$storage[key] = newValue }
  }
  // @DictionaryLike exapnsion ended

}
```

Once we stack up `@COW` and `@DictionaryLike` together on the same type,
then there come to the situation that both `@COW` and `@DictionaryLike`
adds a member called `_$storage` to the applied type.

```swift
@COW
@DictionaryLike
struct User {

  // Other contents ...

  // Brought by @COW's expansion
  var _$storage: Storage

  // Brought by @DictionaryLike's expansion
  var _$storage: [String : Any] = [:]

}
```

This obviously would not get compiled in Swift because Swift does not
allow overloads on properties. We would get “invalid redeclaration of a
variable” again.

TODO: Compilation failure of the code above

### Unique Language Structure Conflicts

The name collision is not the only pitfall of Swift Macro. Some language
structures in Swift are unique under the superstructure. This means when
two macros try to generate the same substructure in the same
superstructure, the code does not compile.

We can contrive this by starting from the previous `@DictionaryLike`
example. Let's consider there is an attached accessor macro called
`@UseDictionaryStorage` which generates `get` and `set` accessor for the
attached property. The getter and setter forward access to the storage
which is brought by the expansion of `@DictionaryLike`.

```swift
@COW
@DictionaryLike
struct User {
  
  @UseDictionaryStorage
  var info: [String : Any]?

}
```

You might think that it would be expanded into:

```swift
@COW
@DictionaryLike
struct User {
  
  @UseDictionaryStorage
  var info: [String : Any]? {
    // @UseDictionaryStorage exapnsion began
    get {
      return _$storage["info"] as? [String : Any]?
    }
    set {
      _$storage["info"] = newValue
    }
    // @UseDictionaryStorage exapnsion ended
  }

}
```

However, that's wrong. With `@COW` macro, the code would be expanded into:

```swift
@COW
@DictionaryLike
struct User {
  
  @UseDictionaryStorage
  @COWIncluded
  var info: [String : Any]? {
    // @COWIncluded expansion began
    get {
      _$storage.info
    }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.info = newValue
    }
    // @COWIncluded expansion ended
    // @UseDictionaryStorage exapnsion began
    get {
      return _$storage["info"] as? [String : Any]?
    }
    set {
      _$storage["info"] = newValue
    }
    // @UseDictionaryStorage exapnsion ended
  }

}
```

And this expansion could not be compiled.

TODO: Previous code snippet does not compile

### Semantics Conflicts

TODO: Paragraph conjunctions.

Some language features could also interfere with attached macros. Look at
the following example: a property wrapper that is attached to a stored
property finally makes a `@COW` attached `struct` not compile:

```swift
@propertyWrapper
struct Capitalized {
  
  var wrappedValue: String {
    didSet {
      wrappedValue = wrappedValue.capitalized
    }
  }
  
}

@COW
struct User {
  
  @Capitalized
  var name: String = ""
  
}
```

Since the property wrapper "expansion" happens later than the macro
expansion, the `struct` would be expanded into:

```swift
@COW
struct User {
  
  @COWIncluded
  @Capitalized
  var name: String = "" {
    get {
      return _$storage.name
    }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.name = newValue
    }
  }

  // ...

}
```

We can observe that the `@Capitalized` property wrapper is still attached
to the `name` variable but the variable is changed from a stored property
into a computed property. Eventually, we would get an error diagnosed by
the compiler:

> Property wrapper cannot be applied to a computed property

TODO: Replace with Xcode screenshot

This does not only happen along with property wrappers, the `lazy` keyword
could also lead to the same end.

```swift
@COW
class User {
  
  lazy var name: String = { "Jane Doe" }()
  
}
```

```swift
@COW
class User {
  
  @COWIncluded
  lazy var name: String = { "Jane Doe" }() {
    get {
      return _$storage.name
    }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.name = newValue
    }
  }

  // ...

}
```

TODO: Replace with Xcode screenshot

With these examples, we can learn that the expansion of a Swift macro
sometimes changes the semantics of the source code. This could lead to a
semantics conflict and ultimately make the macro expansion not compile.

## Overcome the Pitfalls

In the previous section, we've learned typical pitfalls that could be
found in implementing a Swift macro. These pitfalls could be generalized
and categorized into several kinds:

1. The macro expansion occupies non-unique names like `_$storage`.
2. The macro expansion occupies unique names like `get` or `set`.
3. The macro apply site also utilizes unstoppable source code generation
  language features like property wrapper or `lazy` keyword.
4. The macro expansion refers to non-standard-library types, functions or
  variables.

All these pitfalls could be overcome by a set of methods that I called
gradual control over code generation -- which was derived from the concept
of progressive disclosure in API design and the concept of gradual typing.

1. The first level of code generation control is no control which can be
  achieved by using `MacroExpansionContext.makeUniqueName(_:)`.
2. The second level of code generation control is that the code generation
  should be stopped when the name is occupied by the programmer's code.
3. The third level of code generation control is that the programmer can  
  explicitly turn off it.
4. The fourth level of code generation control is that the programmer can
  explicitly customize the name used for code generation.
5. Use the fully-qualified name when referring to non-standard-library
  types, functions or variables.

Let's see how this set of methods works in real examples:

For the first kind of pitfall, we have seen enough examples in the
previous section.

TODO: TBD

The second kind of pitfall could appear when there is an open-source
version of Swift Observation that copied the source code of Swift
Observation but renamed the `@Observable` macro into `@MyObservable` and a
programmer wants to apply both `@Observable` and `@MyObservable` on a
single class:

```swift
@Observable
@MyObservable
class Model {

  var name: String

}
```

This would be expanded into:

```swift
@Observable
@MyObservable
class Model {

  @ObservationTracked
  @MyObservationTracked
  var name: String {
    init(initialValue) initializes (_name) {
      _name = initialValue
    }
    get {
      access(keyPath: \.name)
      return _name
    }
    set {
      withMutation(keyPath: \.name) {
        _name = newValue
      }
    }
    init(initialValue) initializes (_name) {
      _name = initialValue
    }
    get {
      access(keyPath: \.name)
      return _name
    }
    set {
      withMutation(keyPath: \.name) {
        _name = newValue
      }
    }
  }

}
```

Attention, this is not a joke. Since Swift Observation is the killer app
of Swift Macro and Swift Observation requires the minimum deployment
target set to iOS 17.0. As a real example, the community has already built
OpenCombine to use the APIs in Combine on lower versions of iOS.

---

- When the macro expansion occupies non-unique names
  - Compiler-generated names do not make trouble in debugging
    - makeUniqueName
  - Compiler-generated names make trouble in debugging
    - Stop generation when the name was used by the programmer
    - Programmers can explicitly stop the code generation
    - Customizable names
  - Consider moving to a framework type and access with a full-qualified
    name
- The macro expansion occupies unique names (`willSet`, `didSet`)
  - Let the user be able to stop code generation
- The macro expansion refers to non-standard-library names
  - Use full-qualified names

---

### Beyond the Limitations of Freestanding Macro

To fix this potential variable name shadowing for freestanding macros, we
could create a closure and execute it immediately in place:

```swift
func foo(_ bar: Int?) {
  // `updater` defined the first time
  let updater = Updater()
  // #unwrap expansion began
  guard let bar else {
    return true
  }
  { (bar: Int) -> Void in
    // `updater` defined the second time
    let updater = Updater()
    print(bar)
    updater.update()
  }(bar)
  // #unwrap expansion ended
  print(updater.description)
}
```

The manually created closure introduced a lexical scope for the embraced
contents of the macro expansion which prevented the variable name from
being shadowed in previous examples.

But once the body of the closure contains control flows, the closure body
would not get inlined by the optimizer in its performance inlining pass.
This could leave the body of the closure out of the local analysis and
optimization of the macro's apply site. In some cases, this also means to
larger code size. To get rid of this situation, we could use the local
function instead of closure and attribute the local function as
`@inline(__always)`.

```swift
func foo(_ bar: Int?) {
  // `updater` defined the first time
  let updater = Updater()
  // #unwrap expansion began
  guard let bar else {
    return true
  }
  @inline(__always)
  func unwrapped(bar: Int) -> Void {
    // `updater` defined the second time
    let updater = Updater()
    print(bar)
    updater.update()
  }
  unwrapped(bar)
  // #unwrap expansion ended
  print(updater.description)
}
```

However, we can quickly find that once the `#unwrap` macro is applied
twice in a single function, the `unwrapped` function would collide. This
could be solved by using `MacroExpansionContext.makeUniqueName(_:)` to
generate a unique name for the `unwrapped` function.

### Beyond the Limitations of Attached Macros

The issues of the attached macros I shown above are obviously of two
categories:

- Name conflicts brought by sharing the "namespace".
- Semantics conflicts brought by semantics change due to macro expansion.

Dealing with name conflicts brought by the attached macro seems not
difficult since we've done that with freestanding macros. But how to deal
with semantics conflicts?

In the real world, one single macro author cannot predict what names all
other macro authors could pick, and in the real world, invariant semantics
should not be a property of Swift macro expansion, because it could
decrease the flexibility of the language feature. Based on this point, I
concluded a concept to deal with both two issues: gradual control over
code generation -- which is derived from the concept of progressive
disclosure in API design and the concept of gradual typing.

Just let me show you what is "gradual control over code generation" by
example.

We still use the `@COW` example here. The conflicts could be resolved if
we can control `@COW` to generate member names at the programmer's will.
What might be something new to you is this could be done by macro
overloading:

```swift
@COW(storageName: "_$cowStorage")
@DictionaryLike(storageName: "_$dictStorage")
struct User {

  // ...

  // Brought by @COW's expansion
  var _$cowStorage: Storage

  // Brought by @DictionaryLike's expansion
  var _$dictStorage: [String : Any] = [:]

}
```

In the example above, we overloaded `@COW` and `@DictionaryLike` macros to
have a parameter called `storageName` to specify the variable name of the
generated storage of each macro.

`MacroExpansionContext.makeUniqueName(_:)` is not recommended here because
the name generated by `MacroExpansionContext.makeUniqueName(_:)` with real
running compiler instance is a mangled string, which is OK for
freestanding macros debugging but may introduce troubles into attached
macros debugging.

TODO: A real example of generated unique name

But what if there are potential conflicts of
`makeStorageUniqueIfNeeded()`? I mean what if there are two macros

There are the principles that we can learn from what we've done:

1. For generated properties and non-standard library typed generated
   functions brought by attached member macros, we should enable
   programmers to optionally customize its name.
2. For standard library typed generated functions brought by attached
   member macros, we should stop code generation if there has already been
   one.
3. For attached member macros that generate members in type declarations,
   we should always offer an option to disable the code generation for
   specified members by applying an attached member attribute macro.

All these principles fall into a goal that to enable the programmers to
resolve conflicts by themselves. Again,
`MacroExpansionContext.makeUniqueName(_:)` is not recommended here because
it introduces unreadable names which may interfere with debugging.

These principles could also be used for resolving conflicts brought by
semantics changes due to macro expansion:

```swift
import Observation

@Observable
class Model {
  
  // Application of principle 3
  // Resolve conflicts by hand
  @ObservationIgnored
  @Capitalized
  var _name: String = ""
  
  var name: String {
    get {
      access(keyPath: \.name)
      return _name
    }  
    set {
      withMutation(keyPath: \.name) {
        _name = newValue
      }
    }
  }
  
}
```

## Future Directions

We've understood the nature of Swift macro by learning so much more.
But are these limitations still will be there in the future?

From what I've learned, my answer is yes. Because what brings Swift Macro
advantages also brings limitations. These limitations are also a part of
the essence of Swift macro.

But there are several pieces of information that you might not know about
which I collected from Swift evolution proposals and the latest source
code changes in the Swift repository.

### Init Accessor

The `init` accessor is introduced to eliminate the limitation that the
`@Observable` macro Swift Observation requires properties to have initial
values. This change has been bundled with Xcode 15 beta 4:

```swift
import Observation

@Observable
class Model {

  var foo: Int

}
```

The code above is not compiled before Xcode 15 beta 4, but will be
expanded into the following code after it:

```swift
import Observation

@Observable
class Model {

  var _foo: Int

  var foo: Int {
    init(initialValue) initializes(_foo) {
      _foo = initialValue
    }
    get {
      return _foo
    }
    set {
      _foo = newValue
    }
  }
  
  // ...

}
```

### Macro Argument Type Info

The proposal SE-0382 Expression Macros was written that:

> The arguments to a macro are fully type-checked before the macro
> implementation is invoked. However, information produced while
> performing that type-check is not provided to the macro, which only gets
> the original source code. In some cases, it would be useful to also have
> information determined during type checking, such as the types of the
> arguments and their subexpressions, the full names of the declarations
> referenced within those expressions, and any implicit conversions
> performed as part of type checking.

And there is also a comprehensive example in the proposal which is there
could be an `#assert` macro

```swift
#assert(Color(parsing: "red") == .red)
```

That can be expanded into:

```swift
{
  let _unique1 = Color(parsing: "red")
  let _unique2 = .red
  if !(_unique1 == _unique2) {
    fatalError("assertion failed: \(_unique1) != \(_unique2)")
  }
}()
```

Since `let _unique2 = .red` does not have type annotation, the expanded
code would not get compiled. By providing type info for the macro
arguments, specifically about the 'Color' type in this example,
this can be expanded as follows:

```swift
{
  let _unique1: Color = Color(parsing: "red")
  let _unique2: Color = .red
  if !(_unique1 == _unique2) {
    fatalError("assertion failed: \(_unique1) != \(_unique2)")
  }
}()
```

This time the code would get compiled.

But porting Swift type info which retained by the compiler that
implemented in C++ to Swift and make the programming interface to be
simple and ergonomic to most Swift developers is quite a challenging task.
Because there are a lot of detailed information about a type derived by
the compiler which is used for SIL generation and upcoming optimizations.
Macro authors should not care about them.

## Recap

In this post, we explored what existing Swift language features like
function, type and module have managed to do and what the limitations they
have. Then we explored some tasks that Swift macro excels at. Such that we
learned that: Swift macro is yet another encapsulation technique
introduced in Swift which can:

- break control flows in function
- share lexical scope within the call-site function
- share the "name space" within the attached type
- share the namespace within the module

This bring Swift macro to be excelled at some tasks but also bring it
limitations like:

- Name conflicts
- Semantic changes due to macro expansion

To go beyond these limitations, we introduced tips that:

- use in-place executed closure to create a lexical scope
- use chained arguments to eliminate use of local variables
- use `MacroExpansionContext.makeUniqueName(_:)` to create contextual
  unique names

to resolve name conflicts brought by application of freestanding macros.

On top of that, we also introduced principles that:

1. For non-standard library typed members generated by attached member
   macros, we should enable to programmers to optionally customize its
   name.
2. For standard library typed members generated by attached member macros,
   we should stop code generation if there has already been one.
3. For attached member macros that generate members in attached types, we
   should always offer an option to disable the code generation for
   specified members by applying an attached member attribute macro.

to resolve name conflicts and semantics changes brought by application of
attached macros.
